# ============================================================
# issue_prioritizer.py — Tool 3: Prioritize issues by severity
# ============================================================
# PURPOSE:
#   Ranks all issues by severity and impact to help teams
#   focus on the most critical problems first.
#
# INPUT:  Scanner output + test generator output
# OUTPUT: JSON with prioritized issues
# ============================================================

import json


def run(scanner_output, test_output, client, model):
    """Prioritize issues by severity and impact."""
    
    # Parse scanner output
    try:
        scanner_data = json.loads(scanner_output)
        issues = scanner_data.get("issues", [])
        summary = scanner_data.get("summary", {})
    except:
        issues = []
        summary = {}
    
    # Build context about test coverage
    test_context = f"Generated test cases:\n{test_output[:500]}..." if len(test_output) > 500 else test_output
    
    issues_text = "\n".join([
        f"{i+1}. [{issue.get('severity', 'unknown').upper()}] {issue.get('file', 'unknown')} - "
        f"{issue.get('type', 'unknown')}: {issue.get('description', 'No description')}"
        for i, issue in enumerate(issues)
    ])
    
    prompt = f"""You are a senior technical lead doing sprint planning. You must prioritise a backlog of code issues so the team fixes the most dangerous ones first.

## All issues found by the code scanner
{issues_text}

## Test coverage context
{test_context}

## Scanner summary
- Total issues : {summary.get('total_issues', len(issues))}
- Critical      : {summary.get('critical', 0)}
- High          : {summary.get('high', 0)}
- Medium        : {summary.get('medium', 0)}
- Low           : {summary.get('low', 0)}

## Severity definitions — apply these strictly

| Level | Definition |
|---|---|
| **CRITICAL** | Exploitable right now: hardcoded secrets, SQL/command injection, auth bypass, data exfiltration risk |
| **HIGH** | Will cause failures in production: unhandled exceptions on common inputs, missing error handling in critical paths, logic bugs |
| **MEDIUM** | Degrades maintainability or reliability over time: high complexity, missing tests, code duplication |
| **LOW** | Polish and hygiene: missing docstrings, unused imports, naming issues, TODO comments |

## Rules
- Do NOT change severity labels from what the scanner reported unless there is a clear reason stated in "impact".
- Every issue needs a realistic effort estimate: "quick" (< 1 hour), "medium" (half-day), "large" (1+ days).
- Recommendations must be specific action items — not generic advice like "add error handling".
- Output ONLY valid JSON — no markdown fences, no prose.

## Required JSON format
{{
  "critical": [
    {{
      "file": "api.py",
      "issue": "Hardcoded AWS secret key on line 14",
      "impact": "Any user with read access to the repo can steal cloud credentials",
      "effort": "quick"
    }}
  ],
  "high": [],
  "medium": [],
  "low": [],
  "recommendations": [
    "1. Rotate all exposed secrets immediately before touching any code",
    "2. Move credentials to environment variables or a secrets manager",
    "3. Add parameterised queries in db.py to eliminate SQL injection surface"
  ]
}}"""

    # Call the LLM
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )
    
    raw = response.choices[0].message.content
    
    # Parse JSON response
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw
    
    try:
        result = json.loads(raw)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        # Fallback
        return json.dumps({
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "recommendations": ["Review all issues manually"],
            "error": "Failed to parse prioritization",
            "raw_response": raw
        }, indent=2)