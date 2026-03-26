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
    prompt = f"""You are a quality reviewer for a code quality analysis agent.

Review this code quality report and score it on a 1-10 scale.

REPOSITORY: {repo_path}

CODE QUALITY REPORT:
{report}

SCANNER OUTPUT:
{scanner[:500]}...

TEST CASES GENERATED:
{tests[:500]}...

PRIORITIZATION:
{prioritizer[:500]}...

Score each aspect on a 1-10 scale:

1. Issue Detection (1-10):
   - Did it find real, specific issues?
   - Are severity levels accurate?
   - Are descriptions clear and actionable?

2. Test Coverage (1-10):
   - Are generated tests comprehensive?
   - Do they cover edge cases and error conditions?
   - Is the pytest code valid and ready to use?

3. Prioritization (1-10):
   - Are critical issues correctly identified?
   - Is the priority ranking logical?
   - Are recommendations actionable?

4. Report Quality (1-10):
   - Is it well-structured and professional?
   - Are findings clearly communicated?
   - Would a developer know what to fix?

5. Completeness (1-10):
   - Are all critical issues addressed?
   - Is nothing important missing?
   - Does it provide value to the team?

Return ONLY valid JSON (no markdown, no explanation):
{{
  "overall_score": 8,
  "passed": true,
  "aspects": [
    {{"name": "Issue Detection", "score": 8, "note": "Found 5 real issues with clear descriptions"}},
    {{"name": "Test Coverage", "score": 7, "note": "Good edge case coverage"}},
    {{"name": "Prioritization", "score": 8, "note": "Critical issues correctly identified"}},
    {{"name": "Report Quality", "score": 9, "note": "Well-structured and actionable"}},
    {{"name": "Completeness", "score": 7, "note": "All major issues covered"}}
  ],
  "what_is_good": "strengths summary",
  "feedback": "specific improvements needed if score < 7"
}}

RULES:
- overall_score = average of all 5 aspect scores (rounded)
- passed = true if overall_score >= 7
- Minimum requirements for passing:
  * At least 3 issues found
  * At least 2 test cases generated
  * Report has all required sections"""

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
