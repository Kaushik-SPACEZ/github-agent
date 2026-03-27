# MVP Implementation Guide

## Day 1: Build the 4 Tools (6-8 hours)

### Task 1: Create Mock Repository (30 minutes)

Create a sample Python project with intentional code quality issues for testing.

**Files to create**:

```
mock_repo/
├── src/
│   ├── __init__.py
│   ├── main.py          # High complexity, missing error handling
│   ├── utils.py         # Code duplication, no docstrings
│   └── api.py           # Security issues, no input validation
└── tests/
    ├── __init__.py
    └── test_utils.py    # Partial test coverage only
```

**Intentional issues to include**:
- Functions with cyclomatic complexity > 10
- Missing error handling (no try-except)
- No input validation
- Code duplication
- Missing docstrings
- Security issues (hardcoded credentials, SQL injection risks)
- Functions without test coverage

---

### Task 2: Implement code_scanner.py (90 minutes)

**Purpose**: Scan code for bugs, complexity, vulnerabilities, and code smells.

**Input**: Code files from repository  
**Output**: List of issues with severity, location, and description

**Key Features**:
- Detect high complexity functions (cyclomatic complexity)
- Find missing error handling
- Identify security vulnerabilities
- Detect code duplication
- Find missing docstrings
- Flag functions without tests

**Prompt Strategy**:
```python
prompt = f"""You are a senior code reviewer analyzing Python code for quality issues.

Analyze this code and identify:
1. High complexity functions (> 10 branches)
2. Missing error handling (no try-except where needed)
3. Security issues (hardcoded secrets, SQL injection risks)
4. Code duplication
5. Missing docstrings
6. Functions that likely lack test coverage

CODE:
{code_content}

Return a JSON list of issues:
[
  {{
    "type": "complexity",
    "severity": "high",
    "location": "function_name:line_number",
    "description": "specific issue description",
    "suggestion": "how to fix"
  }}
]
"""
```

---

### Task 3: Implement test_case_generator.py (90 minutes)

**Purpose**: Generate pytest test cases for functions that lack coverage.

**Input**: Code files + issues from code_scanner  
**Output**: Ready-to-use pytest test code

**Key Features**:
- Identify functions without tests
- Generate test cases for edge cases
- Include assertions for expected behavior
- Generate both positive and negative test cases

**Prompt Strategy**:
```python
prompt = f"""You are a test engineer writing pytest test cases.

Generate comprehensive test cases for these functions that lack coverage:

FUNCTIONS TO TEST:
{functions_without_tests}

CONTEXT (issues found):
{scanner_issues}

Generate pytest test code with:
1. Test for normal/happy path
2. Test for edge cases
3. Test for error conditions
4. Clear assertions

Return valid Python pytest code that can be copy-pasted into test files.
"""
```

---

### Task 4: Implement issue_prioritizer.py (60 minutes)

**Purpose**: Rank all issues by severity and impact.

**Input**: All issues from code_scanner + test gaps from test_case_generator  
**Output**: Prioritized list (Critical/High/Medium/Low)

**Key Features**:
- Assign severity levels based on impact
- Consider security issues as critical
- Rank by fix urgency
- Group related issues

**Prompt Strategy**:
```python
prompt = f"""You are a technical lead prioritizing code quality issues.

ISSUES FOUND:
{all_issues}

TEST GAPS:
{test_gaps}

Prioritize these issues into 4 categories:
- CRITICAL: Security vulnerabilities, data loss risks
- HIGH: Bugs that affect core functionality
- MEDIUM: Code quality issues, missing tests
- LOW: Style issues, minor improvements

Return JSON:
{{
  "critical": [...],
  "high": [...],
  "medium": [...],
  "low": [...]
}}
"""
```

---

### Task 5: Implement report_writer.py (90 minutes)

**Purpose**: Compile all findings into a structured markdown report.

**Input**: All outputs from previous 3 tools  
**Output**: Comprehensive markdown report

**Key Features**:
- Executive summary
- Issue breakdown by severity
- Generated test cases section
- Recommended actions
- Would-create Jira tickets (mock for MVP)

**Prompt Strategy**:
```python
prompt = f"""You are a technical writer creating a code quality report.

SCAN RESULTS:
{scanner_output}

GENERATED TESTS:
{test_cases}

PRIORITIZED ISSUES:
{prioritized_issues}

Create a comprehensive markdown report with:

# Code Quality Report

## Executive Summary
- Total issues found
- Critical/High/Medium/Low breakdown
- Test coverage gaps
- Overall quality score

## Critical Issues
[List with details]

## High Priority Issues
[List with details]

## Generated Test Cases
[Copy-paste ready pytest code]

## Recommended Actions
[Prioritized list of what to fix first]

## Jira Tickets (Would Create)
[Mock ticket descriptions]

Be specific, actionable, and professional.
"""
```

---

### Task 6: Update planner.py (15 minutes)

**Change**: Update AVAILABLE_TOOLS list

```python
AVAILABLE_TOOLS = [
    {
        "name": "code_scanner",
        "description": "Scan code for bugs, complexity, vulnerabilities, and code smells",
    },
    {
        "name": "test_case_generator",
        "description": "Generate pytest test cases for functions lacking coverage",
    },
    {
        "name": "issue_prioritizer",
        "description": "Rank all issues by severity (Critical/High/Medium/Low)",
    },
    {
        "name": "report_writer",
        "description": "Compile comprehensive code quality report with all findings",
    },
]
```

---

### Task 7: Update executor.py (30 minutes)

**Change**: Add routing for new tools

```python
from agent.tools import code_scanner, test_case_generator, issue_prioritizer, report_writer

def run_plan(plan, repo_path, client, model, on_log):
    results = {}

    for step in plan:
        tool = step["tool"]
        on_log(f"Running tool: {tool} — {step['reason']}")

        if tool == "code_scanner":
            results["code_scanner"] = _run_with_retry(
                lambda: code_scanner.run(repo_path, client, model),
                tool, on_log,
            )

        elif tool == "test_case_generator":
            scanner_output = results.get("code_scanner", "")
            results["test_case_generator"] = _run_with_retry(
                lambda: test_case_generator.run(repo_path, scanner_output, client, model),
                tool, on_log,
            )

        elif tool == "issue_prioritizer":
            scanner_output = results.get("code_scanner", "")
            test_output = results.get("test_case_generator", "")
            results["issue_prioritizer"] = _run_with_retry(
                lambda: issue_prioritizer.run(scanner_output, test_output, client, model),
                tool, on_log,
            )

        elif tool == "report_writer":
            scanner_output = results.get("code_scanner", "")
            test_output = results.get("test_case_generator", "")
            priority_output = results.get("issue_prioritizer", "")
            results["report_writer"] = _run_with_retry(
                lambda: report_writer.run(scanner_output, test_output, priority_output, client, model),
                tool, on_log,
            )

        else:
            on_log(f"Unknown tool: {tool} — skipping")
            continue

        on_log(f"Tool {tool} complete ✓")

    return results
```

---

## Day 2: Integration & Polish (6-8 hours)

### Task 8: Update reviewer.py (60 minutes)

**Change**: Update scoring criteria for code quality reports

```python
def evaluate(repo_path, results, client, model):
    """Score the code quality report."""

    report = results.get("report_writer", "No report generated")
    scanner = results.get("code_scanner", "")
    tests = results.get("test_case_generator", "")

    prompt = f"""You are a quality reviewer for a code quality analysis agent.

Review this code quality report and score it on a 1-10 scale.

REPORT:
{report}

SCANNER OUTPUT:
{scanner}

TEST CASES:
{tests}

Score each aspect:
1. Issue Detection (1-10): Did it find real issues? Are they specific?
2. Test Coverage (1-10): Are generated tests comprehensive?
3. Prioritization (1-10): Are severity levels accurate?
4. Report Quality (1-10): Is it actionable and well-structured?
5. Completeness (1-10): Are all critical issues addressed?

Return JSON:
{{
  "overall_score": 8,
  "passed": true,
  "aspects": [
    {{"name": "Issue Detection", "score": 8, "note": "Found 5 real issues"}},
    {{"name": "Test Coverage", "score": 7, "note": "Good edge case coverage"}},
    ...
  ],
  "what_is_good": "strengths summary",
  "feedback": "specific improvements needed"
}}

PASS_THRESHOLD = 7
"""
```

---

### Task 9: Update main.py UI (90 minutes)

**Changes**:
1. Update title and branding
2. Change input from "idea" to "repository path"
3. Update result tabs for code quality reports
4. Add issue summary visualization
5. Update example button

**Key UI Elements**:
```python
st.markdown('<div class="brand-title">Code Quality Monitor</div>')
st.markdown('<div class="brand-sub">Autonomous AI Agent for Code Analysis</div>')

repo_path = st.text_input(
    "Repository Path or Select Example",
    placeholder="./mock_repo",
)

# Results tabs
tab_summary, tab_tests, tab_report, tab_reasoning = st.tabs([
    "📊 Issue Summary",
    "🧪 Generated Tests", 
    "📄 Full Report",
    "🧠 Agent Reasoning"
])
```

---

### Task 10: Test Full Loop (60 minutes)

**Test Cases**:
1. Run with mock_repo → Should find all intentional issues
2. Test self-review → Should pass on first attempt if prompts are good
3. Test retry logic → Artificially lower threshold to trigger retry
4. Test error handling → Remove API key to test error messages

**Validation Checklist**:
- ✅ All 5 steps complete successfully
- ✅ code_scanner finds 5+ issues
- ✅ test_case_generator creates 3+ tests
- ✅ issue_prioritizer assigns correct severity
- ✅ report_writer produces structured output
- ✅ reviewer scores accurately
- ✅ UI displays results correctly

---

### Task 11: Fix Bugs & Improve Prompts (90 minutes)

**Common Issues**:
- LLM returns invalid JSON → Add JSON validation and retry
- Prompts too vague → Add specific examples
- False positives → Refine detection criteria
- Missing issues → Improve scanner prompt

**Prompt Improvement Strategy**:
```python
# Before (vague)
"Find bugs in this code"

# After (specific)
"Analyze this Python code and identify:
1. Functions with cyclomatic complexity > 10
2. Missing try-except blocks in I/O operations
3. Hardcoded credentials or API keys
4. SQL queries vulnerable to injection
5. Functions longer than 50 lines

For each issue, provide:
- Exact line number
- Severity (critical/high/medium/low)
- Specific description
- Suggested fix"
```

---

### Task 12: Create Demo Video (60 minutes)

**Script**:
1. Introduction (30 sec)
   - "This is an autonomous code quality agent"
   - "It analyzes code without manual intervention"

2. Demo (2 min)
   - Click "Analyze Code Quality"
   - Show 5 steps lighting up
   - Highlight self-review step
   - Show results in all tabs

3. Key Innovation (30 sec)
   - "The agent reviews its own work"
   - "If quality is low, it automatically retries"
   - "This is what makes it autonomous"

4. Future Work (30 sec)
   - "Next: GitHub API integration"
   - "Then: Jira ticket automation"
   - "Finally: React dashboard"

**Recording Tools**:
- OBS Studio (free screen recording)
- Loom (easy sharing)
- Built-in OS screen recording

---

### Task 13: Write Documentation (60 minutes)

**Files to Update**:

1. **README.md**
   - Update title and description
   - Add installation instructions
   - Add usage guide
   - Add demo video link

2. **ARCHITECTURE.md** (new)
   - Explain the 5-step loop
   - Document the 4 tools
   - Show information flow
   - Explain self-review mechanism

3. **DEMO_SCRIPT.md** (new)
   - Step-by-step demo instructions
   - What to say at each step
   - Backup plan if demo breaks

---

## Testing Checklist

### Functional Tests
- [ ] Agent completes full loop without errors
- [ ] code_scanner finds all intentional issues in mock_repo
- [ ] test_case_generator creates valid pytest code
- [ ] issue_prioritizer assigns correct severity levels
- [ ] report_writer produces well-structured markdown
- [ ] reviewer scores accurately (7-9 range for good output)
- [ ] UI displays all results correctly

### Edge Cases
- [ ] Empty repository → Agent handles gracefully
- [ ] Perfect code (no issues) → Agent reports "no issues found"
- [ ] API rate limit → Retry logic works
- [ ] Invalid API key → Clear error message
- [ ] Network error → Graceful failure

### Performance
- [ ] Full analysis completes in < 2 minutes
- [ ] UI remains responsive during analysis
- [ ] Log updates in real-time
- [ ] No memory leaks on multiple runs

---

## Common Issues & Solutions

### Issue: LLM returns invalid JSON

**Solution**:
```python
try:
    result = json.loads(raw_response)
except json.JSONDecodeError:
    # Strip markdown code fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw[:-3]
    result = json.loads(raw.strip())
```

### Issue: code_scanner finds too many false positives

**Solution**: Add confidence scoring
```python
prompt += """
For each issue, also provide a confidence score (0-100):
- 90-100: Definitely a bug
- 70-89: Likely an issue
- 50-69: Possible improvement
- < 50: Ignore

Only return issues with confidence >= 70.
"""
```

### Issue: test_case_generator creates invalid Python

**Solution**: Add syntax validation
```python
import ast

def validate_test_code(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
```

### Issue: Agent always passes review (too lenient)

**Solution**: Raise PASS_THRESHOLD or add stricter criteria
```python
PASS_THRESHOLD = 8  # Instead of 7

# Add minimum requirements
if len(issues_found) < 3:
    return {"passed": False, "feedback": "Need to find more issues"}
```

---

## Post-MVP Enhancements

### Quick Wins (Can add in Day 2 if time permits)

1. **Syntax Highlighting** in UI
   ```python
   st.code(test_cases, language="python")
   ```

2. **Download Report** button
   ```python
   st.download_button("Download Report", report, "report.md")
   ```

3. **Multiple Example Repos**
   ```python
   example = st.selectbox("Example", ["mock_repo", "example_2", "example_3"])
   ```

4. **Issue Statistics Chart**
   ```python
   import plotly.express as px
   fig = px.bar(severity_counts)
   st.plotly_chart(fig)
   ```

---

## Success Criteria

### MVP is complete when:
- ✅ All 4 tools implemented and working
- ✅ Full autonomous loop runs end-to-end
- ✅ Self-review and retry logic works
- ✅ UI displays results in 4 tabs
- ✅ Demo video recorded
- ✅ Documentation updated
- ✅ Ready to present for CP2

### Ready for CP2 demo when:
- ✅ Demo runs smoothly in 3-5 minutes
- ✅ All 5 steps visible in UI
- ✅ Results are impressive (5+ issues, 3+ tests)
- ✅ Can explain the autonomy clearly
- ✅ Have backup video if live demo fails

---

## Time Estimates

| Task | Estimated Time | Priority |
|------|---------------|----------|
| Mock repository | 30 min | High |
| code_scanner | 90 min | High |
| test_case_generator | 90 min | High |
| issue_prioritizer | 60 min | High |
| report_writer | 90 min | High |
| Update planner | 15 min | High |
| Update executor | 30 min | High |
| Update reviewer | 60 min | High |
| Update UI | 90 min | High |
| Testing | 60 min | High |
| Bug fixes | 90 min | Medium |
| Demo video | 60 min | Medium |
| Documentation | 60 min | Medium |
| **TOTAL** | **13.5 hours** | |

**Buffer**: 2.5 hours for unexpected issues  
**Total with buffer**: 16 hours (2 full days)

---

## Next Steps

1. ✅ Read this implementation guide
2. 🔨 Start with Task 1 (mock repository)
3. 🔨 Implement tools in order (Tasks 2-5)
4. 🔨 Update planner and executor (Tasks 6-7)
5. 🔨 Complete Day 2 tasks (Tasks 8-13)
6. 🔨 Test thoroughly
7. 🔨 Record demo
8. 🔨 Submit for CP2

Let's build! 🚀