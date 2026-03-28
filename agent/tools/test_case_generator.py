# ============================================================
# test_case_generator.py — Tool 2: Generate pytest test cases
# ============================================================
# PURPOSE:
#   Generates pytest test cases for functions that lack test coverage.
#
# INPUT:  Repository path + scanner output
# OUTPUT: Python pytest code (ready to copy-paste)
# ============================================================

import os
import json


def run(repo_path, scanner_output, client, model):
    """Generate pytest test cases for untested functions."""
    
    # Parse scanner output
    try:
        scanner_data = json.loads(scanner_output)
        issues = scanner_data.get("issues", [])
    except:
        issues = []
    
    # Collect source code recursively
    python_files = []
    existing_tests = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
        
        for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        rel_path = os.path.relpath(filepath, repo_path)
                        
                        # Separate test files from source files
                        if filename.startswith('test_') or 'test' in root:
                            existing_tests.append(content)
                        else:
                            python_files.append({
                                "filename": rel_path,
                                "content": content
                            })
                except Exception as e:
                    continue
    
    # If no source files, return empty
    if not python_files:
        return "# No Python files found to generate tests for"
    
    # Aggressive limits to stay under 6000 tokens
    # Max 3 files, 800 chars each = ~2400 tokens for code
    python_files = python_files[:3]
    
    files_text = "\n\n".join([
        f"FILE: {f['filename']}\n```python\n{f['content'][:800]}\n```"  # Limit to 800 chars
        for f in python_files
    ])
    
    # Skip existing tests to save tokens
    existing_tests_text = "Existing tests not shown to save space."
    
    # Limit issues to 3
    issues_text = "\n".join([
        f"- {issue.get('file', 'unknown')}: {issue.get('description', 'No description')[:100]}"
        for issue in issues[:3]  # Only 3 issues
    ])
    
    prompt = f"""You are a senior Python test engineer. Your job is to write production-ready pytest test cases.

## Source code to test ({len(python_files)} files)
{files_text}

## Issues already found by the code scanner (prioritise testing these)
{issues_text}

## Task
Write pytest test cases targeting the most critical untested functions — especially any function flagged with a security or reliability issue.

For every function you test, write ALL THREE of:
1. **Happy path** — normal valid inputs, assert the correct output
2. **Edge case** — empty string, None, zero, negative number, empty list, boundary values
3. **Error / security case** — invalid types, malicious input (SQL injection string, path traversal, etc.), assert the right exception is raised with `pytest.raises`

## Rules
- Import only from the actual file paths shown above (e.g. `from src.main import function_name`).
- Use descriptive test function names: `test_<function>_<scenario>`.
- Every test must have a one-line docstring explaining what it verifies.
- Use `assert` with a failure message: `assert result == expected, "reason"`.
- Do NOT write placeholder tests (`assert True`, `pass`).
- Generate at least 6 test functions total.
- Output only the Python code — no prose before or after.

## Output format
```python
import pytest
# real imports here

class TestFunctionName:
    def test_happy_path(self):
        \"\"\"Normal valid input returns expected output.\"\"\"
        ...

    def test_edge_case_none_input(self):
        \"\"\"None input is handled gracefully.\"\"\"
        ...

    def test_security_sql_injection(self):
        \"\"\"Malicious SQL input does not execute raw query.\"\"\"
        ...
```"""

    # Call the LLM
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000,
    )
    
    raw = response.choices[0].message.content
    
    # Extract Python code from markdown if present
    if "```python" in raw:
        start = raw.find("```python") + 9
        end = raw.find("```", start)
        if end != -1:
            raw = raw[start:end].strip()
    elif "```" in raw:
        start = raw.find("```") + 3
        end = raw.find("```", start)
        if end != -1:
            raw = raw[start:end].strip()
    
    return raw