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
    
    prompt = f"""You are a test engineer writing pytest test cases.

SOURCE CODE (showing {len(python_files)} files):
{files_text}

EXISTING TESTS:
{existing_tests_text}

TOP ISSUES FOUND:
{issues_text}

Generate pytest test cases for the MOST CRITICAL untested functions. Focus on:
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