# ============================================================
# report_writer.py — Tool 4: Compile comprehensive report
# ============================================================
# PURPOSE:
#   Synthesizes all findings into a structured markdown report
#   that's ready to share with the development team.
#
# INPUT:  All outputs from previous 3 tools
# OUTPUT: Markdown report
# ============================================================

import json


def run(scanner_output, test_output, priority_output, client, model):
    """Compile comprehensive code quality report."""
    
    # Parse inputs
    try:
        scanner_data = json.loads(scanner_output)
        priority_data = json.loads(priority_output)
    except:
        scanner_data = {}
        priority_data = {}
    
    summary = scanner_data.get("summary", {})
    issues = scanner_data.get("issues", [])
    
    critical = priority_data.get("critical", [])
    high = priority_data.get("high", [])
    medium = priority_data.get("medium", [])
    low = priority_data.get("low", [])
    recommendations = priority_data.get("recommendations", [])
    
    prompt = f"""You are a principal engineer writing a code-quality audit report that will be read by both developers and non-technical stakeholders.

## Data to compile into the report

### Scanner summary
- Files analysed  : {summary.get('files_analyzed', 0)}
- Total issues    : {summary.get('total_issues', 0)}
- Critical        : {summary.get('critical', 0)}
- High            : {summary.get('high', 0)}
- Medium          : {summary.get('medium', 0)}
- Low             : {summary.get('low', 0)}

### Critical issues ({len(critical)} found)
{json.dumps(critical, indent=2)}

### High priority issues ({len(high)} found)
{json.dumps(high, indent=2)}

### Medium priority issues ({len(medium)} found)
{json.dumps(medium, indent=2)}

### Recommended actions
{json.dumps(recommendations, indent=2)}

### Generated test cases
{test_output[:1000]}

## Report requirements

Write a professional markdown report with EXACTLY these sections in this order. Do not skip any section. Do not add extra sections.

---

# Code Quality Audit Report

## Executive Summary
3-5 sentences. State: overall health verdict (healthy / needs attention / critical), total issues found, the single most urgent finding, and one positive observation if any.

## 🔴 Critical Issues  *(must fix before next release)*
For each critical issue:
- **[filename — location]** Issue title
  - **What**: one sentence describing the exact problem
  - **Why it matters**: concrete real-world consequence (data breach, downtime, etc.)
  - **How to fix**: specific code-level instruction, not generic advice

If no critical issues: write "No critical issues found. ✅"

## 🟠 High Priority Issues  *(fix within this sprint)*
Same format as critical. If more than 5, show top 5 and note "and N more."

## 🟡 Medium & Low Priority Issues  *(fix within the quarter)*
Summarise in a short bulleted list — no need for full detail on each.

## 🧪 Generated Test Cases
Paste the test code as a fenced Python block. If no tests were generated, explain why.

## ✅ Recommended Action Plan
Numbered, ordered list — most urgent first. Each item must be a specific task a developer can pick up immediately (not "improve code quality").

## 🎫 Suggested Jira Tickets
Create one ticket per critical and high issue:
- **[PROJ-XX] Title** | Priority: Critical/High | Effort: quick/medium/large
  - Description: one sentence

---

## Writing rules
- Be specific — file names, line numbers, function names wherever possible.
- Avoid filler phrases like "it is important to note" or "in order to".
- Use plain language in the Executive Summary (non-technical readers will read it).
- Use precise technical language in the issue sections (developers will act on it).
- Total length: 500–750 words."""

    # Call the LLM
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
    )
    
    return response.choices[0].message.content