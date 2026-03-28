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

# RAG import — graceful if module not available
try:
    from rag import RAGRetriever
    _RAG_IMPORT_OK = True
except ImportError:
    _RAG_IMPORT_OK = False


def run(repo_path, client, model, uploaded_documents=None):
    """
    Scan code repository for quality issues.
    
    Args:
        repo_path: Path to the repository
        client: Groq client instance
        model: Model name to use
        uploaded_documents: Optional list of uploaded documents to index with RAG
                           Format: [{'filename': 'doc.md', 'content': '...'}]
    """
    
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

    # ── RAG INITIALISATION ────────────────────────────────────────
    # Index the repository into the vector store so each file's
    # analysis prompt can be augmented with similar code patterns.
    # Also index uploaded documents for additional context.
    rag_enabled = False
    rag = None

    if _RAG_IMPORT_OK:
        try:
            rag = RAGRetriever()
            
            # Combine code files and uploaded documents for indexing
            files_to_index = python_files.copy()
            
            if uploaded_documents:
                print(f"[DEBUG] Adding {len(uploaded_documents)} uploaded documents to RAG index...")
                files_to_index.extend(uploaded_documents)
            
            print(f"[DEBUG] Indexing {len(files_to_index)} files with RAG ({len(python_files)} code + {len(uploaded_documents) if uploaded_documents else 0} docs)...")
            rag.index_repository(files_to_index)
            rag_enabled = True
            stats = rag.get_stats()
            print(f"[DEBUG] RAG enabled — {stats['total_embeddings']} embeddings indexed")
            
            if uploaded_documents:
                print(f"[DEBUG] Documents indexed: {', '.join([d['filename'] for d in uploaded_documents])}")
        except Exception as e:
            print(f"[DEBUG] RAG disabled: {e}")
            rag_enabled = False
    else:
        print("[DEBUG] RAG module not available — running without context retrieval")
    # ─────────────────────────────────────────────────────────────
    
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

        # ── RAG CONTEXT RETRIEVAL ─────────────────────────────────
        rag_context = ""
        if rag_enabled and rag:
            try:
                rag_context = rag.get_context_for_file(
                    batch[0]['filename'],
                    issue_type="security vulnerabilities and code quality issues"
                )
                if rag_context:
                    print(f"[DEBUG] RAG context retrieved for {batch[0]['filename']}")
            except Exception as e:
                print(f"[DEBUG] RAG context retrieval failed: {e}")
        # ─────────────────────────────────────────────────────────

        prompt = f"""You are a senior Python security engineer and code reviewer.

Analyse the file below for REAL defects only. DO NOT report false positives.

{rag_context}
## File to analyse
{files_text}

## CRITICAL RULES - READ CAREFULLY:
1. **Only report issues you can ACTUALLY SEE in the code above**
2. **DO NOT hallucinate files that don't exist** (e.g., if you see app.py, don't report issues in auth.py unless auth.py is shown)
3. **DO NOT report normal library imports as security issues** (importing streamlit, dotenv, etc. is NOT insecure deserialization)
4. **DO NOT report issues in code that isn't shown** (if file is truncated, only analyze what you can see)
5. **Every issue MUST reference actual code from the file above** - include the actual line of code in your description

## What to check (only report if you see it):

### 🔴 Security (severity: critical) - ONLY if you see actual vulnerabilities:
- **Hardcoded secrets**: Actual passwords, API keys, tokens visible in the code (e.g., password = "admin123")
- **SQL injection**: String concatenation or f-strings building SQL queries with user input (e.g., query = f"SELECT * FROM users WHERE id = " + user_input)
- **Command injection**: os.system(), subprocess.call() with unsanitized user input, eval() or exec() on user data
- **Insecure deserialization**: pickle.loads() on untrusted data from network/files
- **Sensitive data in logs**: Actual passwords, tokens, or PII being logged (e.g., print(user_password))

### 🟠 Reliability (severity: high) - ONLY if you see actual risks:
- **Missing error handling**: File I/O, network calls, or database operations with no try/except
- **None handling**: Functions that will crash if passed None (e.g., `len(x)` with no None check)
- **Resource leaks**: Files or connections opened but not closed
- **Mutable defaults**: Function parameters with mutable defaults (e.g., `def foo(x=[]):`)

### 🟡 Code Quality (severity: medium) - ONLY if you see actual issues:
- **Long functions**: Functions over 50 lines or with >10 branches
- **Code duplication**: Identical or near-identical code blocks repeated
- **Magic values**: Unexplained numbers or strings (e.g., `if status == 42:`)
- **Missing type hints**: Public functions without type annotations

### 🔵 Maintainability (severity: low) - ONLY if you see actual issues:
- **Missing docstrings**: Public functions/classes without docstrings
- **Unused imports**: Imports that are never used in the code
- **Poor naming**: Single-letter variables outside loops (e.g., `x = calculate_total()`)
- **TODO comments**: TODO/FIXME/HACK comments in the code

## Output rules
- Report ONLY issues you can PROVE exist in the code shown above
- Include the ACTUAL line of code that has the issue in your description
- Every issue MUST reference the exact file shown above (not other files)
- If you can't find at least 2 real issues, that's OK - report what you find
- Maximum 15 issues total
- Return ONLY valid JSON — no markdown, no prose, no explanation

## Required JSON format
{{
  "issues": [
    {{
      "type": "security",
      "severity": "critical",
      "file": "main.py",
      "location": "line 23 — def get_user()",
      "description": "SQL injection: user input concatenated directly into query string",
      "suggestion": "Replace with a parameterised query: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
    }}
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