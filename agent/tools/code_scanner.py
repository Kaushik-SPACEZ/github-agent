# ============================================================
# code_scanner.py — Tool 1: Scan code for bugs and quality issues
# ============================================================
# PURPOSE:
#   Analyzes Python code files to detect bugs, complexity issues,
#   security vulnerabilities, and code smells.
#
# INPUT:  Repository path
# OUTPUT: JSON string with list of issues found
# ============================================================

import os
import json


def run(repo_path, client, model):
    """Scan code repository for quality issues."""
    
    # Collect all Python files
    python_files = []
    src_path = os.path.join(repo_path, "src")
    
    if os.path.exists(src_path):
        for filename in os.listdir(src_path):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(src_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    python_files.append({
                        "filename": filename,
                        "content": content
                    })
    
    # Build the analysis prompt
    files_text = "\n\n".join([
        f"FILE: {f['filename']}\n```python\n{f['content']}\n```"
        for f in python_files
    ])
    
    prompt = f"""You are a senior code reviewer analyzing Python code for quality issues.

Analyze these Python files and identify specific issues:

{files_text}

Identify these types of issues:
1. **High Complexity**: Functions with > 10 conditional branches or deeply nested logic
2. **Missing Error Handling**: File I/O, network calls, or database operations without try-except
3. **Security Issues**: Hardcoded credentials, SQL injection risks, eval() usage, sensitive data in logs
4. **Code Duplication**: Repeated logic that should be refactored
5. **Missing Docstrings**: Functions without documentation
6. **Input Validation**: Missing validation for user inputs or function parameters

For each issue found, provide:
- type: "complexity" | "error_handling" | "security" | "duplication" | "documentation" | "validation"
- severity: "critical" | "high" | "medium" | "low"
- file: filename
- location: "function_name" or "function_name:line_X"
- description: Specific description of the issue
- suggestion: How to fix it

Return ONLY valid JSON (no markdown, no explanation):
{{
  "issues": [
    {{
      "type": "security",
      "severity": "critical",
      "file": "main.py",
      "location": "line 10",
      "description": "Hardcoded database password 'admin123'",
      "suggestion": "Use environment variables or secure vault for credentials"
    }}
  ],
  "summary": {{
    "total_issues": 15,
    "critical": 3,
    "high": 5,
    "medium": 4,
    "low": 3,
    "files_analyzed": 3
  }}
}}"""

    # Call the LLM
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )
    
    raw = response.choices[0].message.content
    
    # Parse JSON response
    raw = raw.strip()
    if raw.startswith("```"):
        # Remove markdown code fences
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw
    
    # Validate and return
    try:
        result = json.loads(raw)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return json.dumps({
            "issues": [],
            "summary": {"total_issues": 0, "error": "Failed to parse LLM response"},
            "raw_response": raw
        }, indent=2)