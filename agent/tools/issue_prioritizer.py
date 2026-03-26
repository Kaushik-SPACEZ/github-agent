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
    
    prompt = f"""You are a technical lead prioritizing code quality issues for a development team.

ISSUES FOUND:
{issues_text}

TEST COVERAGE STATUS:
{test_context}

SUMMARY:
- Total issues: {summary.get('total_issues', len(issues))}
- Critical: {summary.get('critical', 0)}
- High: {summary.get('high', 0)}
- Medium: {summary.get('medium', 0)}
- Low: {summary.get('low', 0)}

Prioritize these issues into 4 categories based on:
- **CRITICAL**: Security vulnerabilities, data loss risks, hardcoded credentials, SQL injection
- **HIGH**: Bugs affecting core functionality, missing error handling in critical paths
- **MEDIUM**: Code quality issues, missing tests, high complexity
- **LOW**: Style issues, minor improvements, missing docstrings

For each category, list the top issues with:
- file: filename
- issue: brief description
- impact: why this matters
- effort: "quick" | "medium" | "large" (estimated fix time)

Return ONLY valid JSON (no markdown):
{{
  "critical": [
    {{
      "file": "main.py",
      "issue": "Hardcoded database password",
      "impact": "Security breach risk - credentials exposed in code",
      "effort": "quick"
    }}
  ],
  "high": [...],
  "medium": [...],
  "low": [...],
  "recommendations": [
    "Fix all critical security issues immediately",
    "Add error handling to database operations",
    "Generate tests for uncovered functions"
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