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
    
    # Collect source code
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
    
    # Check existing tests
    test_path = os.path.join(repo_path, "tests")
    existing_tests = []
    if os.path.exists(test_path):
        for filename in os.listdir(test_path):
            if filename.startswith("test_") and filename.endswith(".py"):
                filepath = os.path.join(test_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_tests.append(f.read())
    
    files_text = "\n\n".join([
        f"FILE: {f['filename']}\n```python\n{f['content']}\n```"
        for f in python_files
    ])
    
    existing_tests_text = "\n\n".join([
        f"```python\n{test}\n```" for test in existing_tests
    ]) if existing_tests else "No existing tests found."
    
    issues_text = "\n".join([
        f"- {issue.get('file', 'unknown')}: {issue.get('description', 'No description')}"
        for issue in issues[:10]  # Limit to first 10 issues
    ])
    
    prompt = f"""You are a test engineer writing pytest test cases.

SOURCE CODE:
{files_text}

EXISTING TESTS:
{existing_tests_text}

ISSUES FOUND BY CODE SCANNER:
{issues_text}

Generate comprehensive pytest test cases for functions that lack coverage. Focus on:
1. Functions without any tests
2. Functions with security issues (test edge cases and malicious inputs)
3. Functions with high complexity (test all branches)
4. Functions with missing error handling (test error conditions)

For each function, generate:
- Test for normal/happy path
- Test for edge cases (empty inputs, None, invalid types)
- Test for error conditions (if applicable)
- Clear assertions with descriptive messages

Return valid Python pytest code that can be copy-pasted into a test file.
Include imports, test functions with descriptive names, and docstrings.

Format:
```python
import pytest
from src.module import function_name

def test_function_name_normal_case():
    \"\"\"Test function with valid inputs.\"\"\"
    result = function_name(valid_input)
    assert result == expected_output, "Description"

def test_function_name_edge_case():
    \"\"\"Test function with edge case.\"\"\"
    # Test code here
    
def test_function_name_error_case():
    \"\"\"Test function error handling.\"\"\"
    with pytest.raises(ExpectedError):
        function_name(invalid_input)
```

Generate at least 3-5 test functions for the most critical untested functions."""

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