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
    
    # Format issues in a more readable way for the LLM
    critical_text = ""
    if critical:
        for i, issue in enumerate(critical, 1):
            critical_text += f"\n{i}. File: {issue.get('file', 'unknown')}\n"
            critical_text += f"   Issue: {issue.get('issue', 'No description')}\n"
            critical_text += f"   Impact: {issue.get('impact', 'Not specified')}\n"
            critical_text += f"   Effort: {issue.get('effort', 'Not specified')}\n"
    else:
        critical_text = "\nNone found."
    
    high_text = ""
    if high:
        for i, issue in enumerate(high, 1):
            high_text += f"\n{i}. File: {issue.get('file', 'unknown')}\n"
            high_text += f"   Issue: {issue.get('issue', 'No description')}\n"
            high_text += f"   Impact: {issue.get('impact', 'Not specified')}\n"
            high_text += f"   Effort: {issue.get('effort', 'Not specified')}\n"
    else:
        high_text = "\nNone found."
    
    medium_text = ""
    if medium:
        for i, issue in enumerate(medium, 1):
            medium_text += f"\n{i}. File: {issue.get('file', 'unknown')}\n"
            medium_text += f"   Issue: {issue.get('issue', 'No description')}\n"
    else:
        medium_text = "\nNone found."
    
    low_text = ""
    if low:
        for i, issue in enumerate(low, 1):
            low_text += f"\n{i}. File: {issue.get('file', 'unknown')}\n"
            low_text += f"   Issue: {issue.get('issue', 'No description')}\n"
    else:
        low_text = "\nNone found."
    
    recommendations_text = ""
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            recommendations_text += f"\n{i}. {rec}"
    else:
        recommendations_text = "\nNo specific recommendations provided."

    prompt = f"""You are a principal engineer writing a code-quality audit report that will be read by both developers and non-technical stakeholders.

## IMPORTANT: You MUST use the actual data provided below. Do NOT make up generic content.

## Scanner Summary
- Files analysed  : {summary.get('files_analyzed', 0)}
- Total issues    : {summary.get('total_issues', 0)}
- Critical        : {summary.get('critical', 0)}
- High            : {summary.get('high', 0)}
- Medium          : {summary.get('medium', 0)}
- Low             : {summary.get('low', 0)}

## Critical Issues Found: {len(critical)}
{critical_text}

## High Priority Issues Found: {len(high)}
{high_text}

## Medium Priority Issues Found: {len(medium)}
{medium_text}

## Low Priority Issues Found: {len(low)}
{low_text}

## Recommended Actions
{recommendations_text}

## Generated Test Cases (first 1000 chars)
{test_output[:1000]}

---

## YOUR TASK

Write a professional markdown report with EXACTLY these sections. You MUST include ALL issues listed above - do not skip any.

# Code Quality Audit Report

## Executive Summary
Write 3-5 sentences stating:
1. Overall health verdict based on the {len(critical)} critical, {len(high)} high, {len(medium)} medium, {len(low)} low issues found
2. The single most urgent finding from the critical/high issues above
3. One positive observation if any

## 🔴 Critical Issues  *(must fix before next release)*

CRITICAL: There are {len(critical)} critical issue(s). You MUST list each one below.

{"For each critical issue listed above, write:" if critical else "Write: No critical issues found. ✅"}
- **[filename]** Issue title
  - **What**: Describe the exact problem from the data above
  - **Why it matters**: Explain the real-world consequence
  - **How to fix**: Provide specific code-level instruction

## 🟠 High Priority Issues  *(fix within this sprint)*

IMPORTANT: There are {len(high)} high priority issue(s). You MUST list each one below.

{"For each high priority issue listed above, write the same format as critical issues." if high else "Write: No high priority issues found."}

## 🟡 Medium & Low Priority Issues  *(fix within the quarter)*

There are {len(medium)} medium and {len(low)} low priority issues. Summarize them in a bulleted list:
{"- List each medium and low issue from the data above" if (medium or low) else "- No medium or low priority issues found."}

## 🧪 Generated Test Cases

```python
{test_output if test_output.strip() else "# No test cases were generated"}
```

## ✅ Recommended Action Plan

Based on the recommendations provided above, create a numbered list of specific tasks:
{recommendations_text if recommendations else "1. Review all issues manually\n2. Prioritize fixes based on severity"}

## 🎫 Suggested Jira Tickets

Create one ticket per critical and high issue from the data above:
{"- List each critical and high issue as a Jira ticket with format: **[PROJ-XX] Title** | Priority: Critical/High | Effort: quick/medium/large" if (critical or high) else "No critical or high priority issues require Jira tickets."}

---

## CRITICAL RULES
1. You MUST include EVERY issue from the data above - do not skip any
2. If there are {len(critical)} critical issues, your report MUST show all {len(critical)} of them
3. If there are {len(high)} high issues, your report MUST show all {len(high)} of them
4. Do NOT write "No critical issues found" if critical issues exist in the data
5. Be specific with file names and descriptions from the actual data provided
6. Total length: 500–750 words"""

    # Call the LLM
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
    )
    
    return response.choices[0].message.content