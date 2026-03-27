# ============================================================
# executor.py — Routes plan steps to tool functions
# ============================================================
# PURPOSE:
#   The executor takes the JSON plan from planner.py and runs each
#   step by calling the correct tool function. It is the "hands"
#   of the agent — it does the actual work.
#
# INFORMATION FLOW (4-tool pipeline):
#   problem_definer    → only needs the idea (first in chain)
#   solution_architect → needs idea + problem analysis
#   idea_challenger    → needs idea + problem + solution (challenges both)
#   submission_writer  → needs EVERYTHING including challenger output
#
# RESILIENCE:
#   Each tool call is wrapped in retry logic with exponential backoff.
#
# HOW TO CUSTOMISE (vibe coding prompt):
#   "Add a new elif branch in executor.py for a tool called
#    market_validator. Import it from agent.tools.market_validator
#    and pass it the idea and problem_definer results."
# ============================================================

import time
import os

from agent.tools import code_scanner, test_case_generator, issue_prioritizer, report_writer

# ── RETRY CONFIGURATION ─────────────────────────────────────────
MAX_RETRIES = 2
RETRY_DELAY = 2


def _run_with_retry(fn, tool_name, on_log):
    """Run a tool function with retry logic for transient API errors."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt <= MAX_RETRIES:
                wait = RETRY_DELAY * (2 ** (attempt - 1))
                on_log(f"Tool {tool_name} error (attempt {attempt}): {e} — retrying in {wait}s...")
                time.sleep(wait)
            else:
                on_log(f"Tool {tool_name} failed after {attempt} attempts: {e}")
                raise last_error


def run_plan(plan, repo_path, client, model, on_log):
    """Execute each step in the plan by routing to the correct tool."""

    results = {}
    
    on_log(f"[DEBUG] Repository path: {repo_path}")
    on_log(f"[DEBUG] Checking if path exists: {os.path.exists(repo_path)}")
    if os.path.exists(repo_path):
        import glob
        py_files = glob.glob(os.path.join(repo_path, "**/*.py"), recursive=True)
        on_log(f"[DEBUG] Python files found: {len(py_files)}")

    for step in plan:
        tool = step["tool"]
        on_log(f"Running tool: {tool} — {step['reason']}")

        # ── ROUTE TO THE CORRECT TOOL ────────────────────────────────
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
