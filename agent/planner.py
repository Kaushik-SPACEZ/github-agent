# ============================================================
# planner.py — Creates a JSON execution plan from goal + feedback
# ============================================================
# PURPOSE:
#   The planner asks the LLM to create a step-by-step action plan
#   in JSON format. It tells the LLM what tools are available and
#   lets the LLM decide the order and reasoning for each step.
#
# THE PLANNING PATTERN:
#   An autonomous agent doesn't just "do stuff" — it first PLANS
#   what to do. The plan is a list of tool calls in order. This is
#   what separates an agent from a chatbot: the agent decides its
#   own workflow before executing it.
#
# HOW TO CUSTOMISE (vibe coding prompt):
#   "Add a new tool to AVAILABLE_TOOLS in planner.py called
#    market_validator with a description. Then add the routing
#    in executor.py."
# ============================================================

import json

# ── AVAILABLE TOOLS ──────────────────────────────────────────────
# This list tells the LLM what tools exist. When you add a new tool
# file in agent/tools/, you MUST also add it here — otherwise the
# planner won't know it exists and will never include it in a plan.
AVAILABLE_TOOLS = [
    {
        "name": "code_scanner",
        "description": "Scan code repository for bugs, complexity issues, security vulnerabilities, and code smells",
    },
    {
        "name": "test_case_generator",
        "description": "Generate pytest test cases for functions that lack test coverage",
    },
    {
        "name": "issue_prioritizer",
        "description": "Rank all issues by severity (Critical/High/Medium/Low) and provide fix recommendations",
    },
    {
        "name": "report_writer",
        "description": "Compile comprehensive code quality report with all findings, test cases, and actionable recommendations",
    },
]


def create_plan(idea, feedback, client, model):
    """Ask the LLM to generate a JSON execution plan for the given idea."""

    # ── BUILD THE PROMPT ─────────────────────────────────────────
    feedback_section = ""
    if feedback:
        feedback_section = f"""
FEEDBACK FROM PREVIOUS ATTEMPT (use this to improve the plan):
{feedback}
"""

    tools_description = "\n".join(
        [f'  - {t["name"]}: {t["description"]}' for t in AVAILABLE_TOOLS]
    )

    prompt = f"""You are the planning engine of an autonomous code-quality monitoring agent.

Your job is to produce a strict 4-step JSON execution plan — nothing else.

## Context
- Repository to analyse: {idea}
- Each step must use exactly one tool from the list below.
- Steps execute sequentially; each step's output feeds the next.
{feedback_section}
## Available Tools
{tools_description}

## Fixed Execution Order (never change this)
1. code_scanner       — must run first; discovers all issues
2. test_case_generator — uses scanner output to target untested/vulnerable code
3. issue_prioritizer  — ranks issues found by the scanner
4. report_writer      — synthesises ALL previous outputs into final report

## Instructions
- Write a specific, honest "reason" for each step explaining WHY it is needed for THIS repository.
- Do NOT invent extra steps or skip any step.
- Output ONLY the JSON array below — no prose, no markdown fences, no explanation.

## Required Output Format
[
  {{"step": 1, "tool": "code_scanner",        "reason": "<specific reason>"}},
  {{"step": 2, "tool": "test_case_generator", "reason": "<specific reason>"}},
  {{"step": 3, "tool": "issue_prioritizer",   "reason": "<specific reason>"}},
  {{"step": 4, "tool": "report_writer",       "reason": "<specific reason>"}}
]"""

    # ── CALL THE LLM ─────────────────────────────────────────────
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )

    raw = response.choices[0].message.content

    # ── PARSE THE JSON ───────────────────────────────────────────
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    plan = json.loads(raw)
    return plan