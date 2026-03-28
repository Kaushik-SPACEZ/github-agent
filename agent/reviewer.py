# ============================================================
# reviewer.py — Scores CP1 draft with FIELD-LEVEL breakdown
# ============================================================
# PURPOSE:
#   The reviewer is what makes this an AUTONOMOUS agent instead of
#   a chatbot. It scores the CP1 draft against the actual 6-field
#   form requirements and decides pass or retry.
#
#   UPGRADE: Now returns per-field scores so the UI can show
#   exactly which fields passed and which need improvement.
#
# CP1 FORM FIELDS IT CHECKS:
#   Field 1: Problem Statement   (min 50 chars, specific pain point)
#   Field 2: Target Users        (min 10 chars, specific segment)
#   Field 3: Autonomy Loop Plan  (min 50 chars, maps THINK/PLAN/EXECUTE/REVIEW/UPDATE)
#   Field 4: Tools & APIs        (comma-separated, realistic stack)
#   Field 5: Evaluation Logic    (min 20 chars, measurable criteria)
#   Field 6: Expected Output     (min 20 chars, concrete deliverable)
#
# HOW TO CUSTOMISE (vibe coding prompt):
#   "Make the reviewer stricter — require score 9 to pass instead
#    of 7. Check that the Autonomy Loop Plan mentions all 5 steps
#    explicitly (THINK, PLAN, EXECUTE, REVIEW, UPDATE)."
# ============================================================

import json

# ── PASS THRESHOLD ───────────────────────────────────────────────
# Score 7+ = pass. Below 7 = the agent retries with feedback.
PASS_THRESHOLD = 7

# ── FIELD DEFINITIONS ────────────────────────────────────────────
FIELDS = [
    {"id": 1, "name": "Problem Statement", "min_chars": 50},
    {"id": 2, "name": "Target Users", "min_chars": 10},
    {"id": 3, "name": "Autonomy Loop Plan", "min_chars": 50},
    {"id": 4, "name": "Tools & APIs", "min_chars": 1},
    {"id": 5, "name": "Evaluation Logic", "min_chars": 20},
    {"id": 6, "name": "Expected Output", "min_chars": 20},
]


def evaluate(repo_path, results, client, model):
    """Score the code quality report."""

    report = results.get("report_writer", "No report generated")
    scanner = results.get("code_scanner", "")
    tests = results.get("test_case_generator", "")
    prioritizer = results.get("issue_prioritizer", "")

    # ── BUILD THE PROMPT ─────────────────────────────────────────
    prompt = f"""You are a senior engineering manager reviewing an automated code-quality report before it is sent to a development team.

Your job: score the report objectively and decide whether it meets the quality bar to be delivered.

## Inputs to review
- Repository analysed: {repo_path}
- Code scanner output (issues found):
{scanner[:800]}

- Test cases generated:
{tests[:600]}

- Issue prioritisation:
{prioritizer[:600]}

- Final compiled report:
{report[:1200]}

## Scoring rubric — rate each aspect 1-10

| Aspect | What "10" looks like |
|---|---|
| Issue Detection | Every real bug/vuln found; zero false positives; each issue has file + line + clear description |
| Test Coverage | Tests cover happy path, edge cases, and error conditions for every flagged function |
| Prioritisation | CRITICAL/HIGH/MEDIUM/LOW labels are accurate; fix-effort estimates are realistic |
| Report Clarity | A developer reading it knows exactly what to fix, in what order, and why |
| Completeness | Nothing important is missing; all sections are populated with real content |

## Minimum passing requirements (score must be >= {PASS_THRESHOLD})
- At least 3 distinct issues found with file locations
- At least 2 working pytest test functions generated
- Report contains Executive Summary, Critical Issues, and Recommended Actions sections
- No section is filled with placeholder or generic text

## Output — return ONLY valid JSON, no markdown fences, no extra text
{{
  "overall_score": <integer 1-10, average of the 5 aspects>,
  "passed": <true if overall_score >= {PASS_THRESHOLD} else false>,
  "aspects": [
    {{"name": "Issue Detection",   "score": <1-10>, "note": "<one specific observation>"}},
    {{"name": "Test Coverage",     "score": <1-10>, "note": "<one specific observation>"}},
    {{"name": "Prioritisation",    "score": <1-10>, "note": "<one specific observation>"}},
    {{"name": "Report Clarity",    "score": <1-10>, "note": "<one specific observation>"}},
    {{"name": "Completeness",      "score": <1-10>, "note": "<one specific observation>"}}
  ],
  "what_is_good": "<2-3 sentences on genuine strengths to preserve in the next attempt>",
  "feedback": "<if score < {PASS_THRESHOLD}: concrete, specific improvements the agent must make — not generic advice>"
}}"""

    # ── CALL THE LLM ─────────────────────────────────────────────
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )

    raw = response.choices[0].message.content

    # ── PARSE THE JSON ───────────────────────────────────────────
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    review = json.loads(raw)

    # ── ENFORCE THRESHOLD ────────────────────────────────────────
    score = review.get("overall_score", review.get("score", 0))
    review["score"] = score
    review["passed"] = score >= PASS_THRESHOLD

    return review