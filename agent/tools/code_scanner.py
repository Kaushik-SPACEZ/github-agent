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
    
    # Collect all Python files recursively
    python_files = []
    
    print(f"[DEBUG] Scanning repository: {repo_path}")
    print(f"[DEBUG] Repository exists: {os.path.exists(repo_path)}")
    
    for root, dirs, files in os.walk(repo_path):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
        
        for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Get relative path for better display
                        rel_path = os.path.relpath(filepath, repo_path)
                        python_files.append({
                            "filename": rel_path,
                            "content": content
                        })
                        print(f"[DEBUG] Found Python file: {rel_path} ({len(content)} chars)")
                except Exception as e:
                    # Skip files that can't be read
                    print(f"[DEBUG] Error reading {filepath}: {e}")
                    continue
    
    print(f"[DEBUG] Total Python files found: {len(python_files)}")
    
    # If no files found, return empty result
    if not python_files:
        return json.dumps({
            "issues": [],
            "summary": {
                "total_issues": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "files_analyzed": 0
            }
        }, indent=2)
    
    # Process files in batches to avoid token limits
    # Reduce batch size to handle large files - process 1 file at a time
    batch_size = 1
    all_issues = []
    files_analyzed = 0
    
    for i in range(0, len(python_files), batch_size):
        batch = python_files[i:i + batch_size]
        files_text = "\n\n".join([
            f"FILE: {f['filename']}\n```python\n{f['content']}\n```"
            for f in batch
        ])
        
        # For very large files, truncate to first 2000 chars to stay under token limit
        file_content = batch[0]['content']
        if len(file_content) > 2000:
            files_text = f"FILE: {batch[0]['filename']}\n```python\n{file_content[:2000]}\n... (file truncated for analysis)\n```"
            print(f"[DEBUG] File {batch[0]['filename']} truncated from {len(file_content)} to 2000 chars")
        
        prompt = f"""Analyze this Python file for issues. Find AT LEAST 2-3 issues per file.

{files_text}

Check for:
1. Security: hardcoded credentials, SQL injection, eval(), sensitive data in logs
2. Error handling: missing try-except for file I/O, network, database ops
3. Code quality: missing docstrings, type hints, magic numbers, long functions
4. Best practices: naming, comments, duplication, unused imports

Return ONLY JSON:
{{
  "issues": [
    {{"type": "security", "severity": "critical", "file": "main.py", "location": "line 10", "description": "Issue here", "suggestion": "Fix here"}}
  ]
}}"""

        # Call the LLM for this batch
        print(f"[DEBUG] Calling LLM for batch {i//batch_size + 1}...")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            
            raw = response.choices[0].message.content
            print(f"[DEBUG] LLM response received, length: {len(raw)} chars")
            
            # Parse JSON response - handle markdown code fences
            raw = raw.strip()
            
            # Remove markdown code fences if present
            if raw.startswith("```json"):
                raw = raw[7:]  # Remove ```json
            elif raw.startswith("```"):
                raw = raw[3:]  # Remove ```
            
            if raw.endswith("```"):
                raw = raw[:-3]  # Remove closing ```
            
            raw = raw.strip()
            
            # If response starts with text before JSON, extract just the JSON
            if not raw.startswith("{"):
                # Find the first { and extract from there
                json_start = raw.find("{")
                if json_start != -1:
                    raw = raw[json_start:]
            
            # Find the last } to handle extra text after JSON
            # Count braces to find the matching closing brace
            brace_count = 0
            json_end = -1
            for idx, char in enumerate(raw):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = idx + 1
                        break
            
            if json_end != -1:
                raw = raw[:json_end]
            
            # Parse and collect issues
            batch_result = json.loads(raw)
            print(f"[DEBUG] LLM returned {len(batch_result.get('issues', []))} issues")
            print(f"[DEBUG] Raw LLM response preview: {raw[:500]}...")
            
            if "issues" in batch_result:
                all_issues.extend(batch_result["issues"])
                print(f"[DEBUG] Total issues collected so far: {len(all_issues)}")
            files_analyzed += len(batch)
            
        except Exception as e:
            # Skip this batch if it fails
            print(f"[DEBUG] ERROR in batch processing: {e}")
            print(f"[DEBUG] Exception type: {type(e).__name__}")
            try:
                print(f"[DEBUG] Raw response (if available): {raw[:500]}...")
            except:
                print(f"[DEBUG] Could not print raw response")
            continue
    
    # Aggregate results from all batches
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in all_issues:
        severity = issue.get("severity", "low")
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    final_result = {
        "issues": all_issues,
        "summary": {
            "total_issues": len(all_issues),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
            "files_analyzed": files_analyzed
        }
    }
    
    return json.dumps(final_result, indent=2)
