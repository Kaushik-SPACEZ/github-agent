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

    prompt = f"""You are a planning engine for an autonomous code quality monitoring agent.

GOAL: Analyze code repository for quality issues, generate test cases, prioritize findings, and create comprehensive report.

REPOSITORY PATH: {idea}
{feedback_section}
AVAILABLE TOOLS:
{tools_description}

Create an execution plan with exactly 4 steps, one per tool.
Order: code_scanner → test_case_generator → issue_prioritizer → report_writer
The report_writer MUST be last (it synthesises all previous outputs).

Return ONLY valid JSON — no markdown, no explanation, no extra text.
Use this exact format:
[
  {{"step": 1, "tool": "code_scanner", "reason": "why this step"}},
  {{"step": 2, "tool": "test_case_generator", "reason": "why this step"}},
  {{"step": 3, "tool": "issue_prioritizer", "reason": "why this step"}},
  {{"step": 4, "tool": "report_writer", "reason": "why this step"}}
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
