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
    
    prompt = f"""You are a technical writer creating a professional code quality report.

SCAN SUMMARY:
- Total issues: {summary.get('total_issues', 0)}
- Critical: {summary.get('critical', 0)}
- High: {summary.get('high', 0)}
- Medium: {summary.get('medium', 0)}
- Low: {summary.get('low', 0)}
- Files analyzed: {summary.get('files_analyzed', 0)}

CRITICAL ISSUES ({len(critical)}):
{json.dumps(critical, indent=2)}

HIGH PRIORITY ISSUES ({len(high)}):
{json.dumps(high, indent=2)}

MEDIUM PRIORITY ISSUES ({len(medium)}):
{json.dumps(medium, indent=2)}

GENERATED TEST CASES:
{test_output[:800]}...

RECOMMENDATIONS:
{json.dumps(recommendations, indent=2)}

Create a comprehensive markdown report with these sections:

# Code Quality Analysis Report

## Executive Summary
- Brief overview of findings
- Overall quality assessment
- Key metrics

## Critical Issues ⚠️
List each critical issue with:
- File and location
- Description
- Why it's critical
- Suggested fix

## High Priority Issues
List high priority issues (top 5 if more than 5)

## Medium Priority Issues
Summarize medium issues (don't list all if > 10)

## Generated Test Cases 🧪
Show the pytest code that was generated (formatted as code block)

## Recommended Actions
Prioritized list of what to fix first

## Jira Tickets (Would Create)
For each critical and high issue, show what Jira ticket would be created:
- Ticket title
- Description
- Priority
- Assignee suggestion (based on file ownership)

Be specific, actionable, and professional. Use emojis sparingly for visual clarity.
Total length: 400-600 words."""

    # Call the LLM
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
    )
    
    return response.choices[0].message.content