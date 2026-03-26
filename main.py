# ============================================================
# main.py — Streamlit UI for Code Quality Monitor
# ============================================================
# PURPOSE:
#   This file is the user interface ONLY. It renders the Streamlit
#   web app with step cards, a log box, and the code quality report.
#   All agent logic lives in agent/loop.py — this file just handles
#   display and user input.
#
# UI-ONLY RULE:
#   Do not put agent logic, LLM calls, or tool functions in this
#   file. main.py calls agent.loop.run() and displays the results.
#   That's it.
# ============================================================

import os
import datetime
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from agent import loop

# ── LOAD ENVIRONMENT ─────────────────────────────────────────────
load_dotenv()

# ── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Code Quality Monitor — Autonomous AI Agent",
    page_icon="🔍",
    layout="wide",
)

# ── CUSTOM CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Step cards */
    .step-card {
        border-radius: 10px;
        padding: 16px 8px;
        text-align: center;
        margin: 4px;
        font-size: 14px;
        min-height: 110px;
        transition: all 0.3s ease;
    }
    .step-pending {
        background-color: #f0f0f0;
        border: 2px solid #cccccc;
        color: #888888;
    }
    .step-active {
        background-color: #fff8e1;
        border: 2px solid #ffc107;
        color: #f57f17;
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.3); }
        50% { box-shadow: 0 0 12px 4px rgba(255, 193, 7, 0.3); }
    }
    .step-done {
        background-color: #e8f5e9;
        border: 2px solid #4caf50;
        color: #1b5e20;
    }
    .step-failed {
        background-color: #ffebee;
        border: 2px solid #f44336;
        color: #b71c1c;
    }
    .step-skipped {
        background-color: #f3e5f5;
        border: 2px solid #9c27b0;
        color: #4a148c;
    }

    /* Activity log */
    .log-box {
        background-color: #1E1E2E;
        color: #cdd6f4;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        padding: 12px;
        border-radius: 8px;
        max-height: 220px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .log-time { color: #6c7086; }
    .log-tool { color: #89b4fa; }
    .log-pass { color: #a6e3a1; }
    .log-fail { color: #f38ba8; }
    .log-loop { color: #cba6f7; font-weight: bold; }

    /* Branding */
    .brand-title {
        text-align: center;
        font-size: 2.4em;
        font-weight: 800;
        background: linear-gradient(135deg, #dc2626, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .brand-sub {
        text-align: center;
        font-size: 1.05em;
        color: #64748b;
        margin-top: 2px;
        margin-bottom: 4px;
    }
    .brand-badge {
        text-align: center;
        margin-bottom: 16px;
    }
    .brand-badge span {
        background-color: #dc2626;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Loop counter */
    .loop-counter {
        text-align: center;
        background-color: #1E1E2E;
        color: #cba6f7;
        padding: 8px 16px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 14px;
        margin: 8px 0;
    }

    /* Score card */
    .score-card {
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        font-weight: bold;
    }
    .score-pass {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border: 2px solid #4caf50;
        color: #1b5e20;
    }
    .score-fail {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border: 2px solid #f44336;
        color: #b71c1c;
    }

    /* Tool pipeline */
    .pipeline-card {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-size: 13px;
    }
    
    /* Issue badge */
    .issue-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    .badge-critical {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }
    .badge-high {
        background-color: #fed7aa;
        color: #9a3412;
        border: 1px solid #fdba74;
    }
    .badge-medium {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    .badge-low {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #93c5fd;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER & BRANDING ───────────────────────────────────────────
st.markdown('<div class="brand-title">Code Quality Monitor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-sub">Autonomous AI Agent for Code Analysis</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="brand-badge"><span>STUDAI FOUNDRY — AUTONOMOUS AI HACKATHON</span></div>',
    unsafe_allow_html=True,
)

# ── AUTONOMY EXPLAINER ──────────────────────────────────────────
with st.expander("🤖 What makes this AUTONOMOUS (not a chatbot)?", expanded=False):
    st.markdown("""
**A chatbot** takes your input → calls an LLM once → returns whatever it gets. One shot. Done. No quality check.

**An autonomous agent** takes your *goal* and then:

| Step | What the Agent Does | Why It Matters |
|------|-------------------|---------------|
| **THINK** | Parses the repository path + any feedback from previous attempts | Context awareness — understands what needs improvement |
| **PLAN** | Asks the LLM to create a JSON action plan | Self-directed — it decides *what* to do, not you |
| **EXECUTE** | Runs 4 tools in sequence (scan → test → prioritize → report) | Tool use — each tool does one job, outputs chain together |
| **REVIEW** | Scores its own output 1-10 against quality criteria | **Self-evaluation — THIS is what makes it autonomous** |
| **UPDATE** | If score < 7, carries feedback into the next loop | Self-correction — it learns from its own mistakes |

The loop runs up to **3 times**. Each retry uses specific feedback to improve. This is the exact same architecture used in production AI agents — the domain changes, the loop doesn't.

**4-Tool Pipeline:**
1. **Code Scanner** → Detects bugs, complexity, security issues, code smells
2. **Test Case Generator** → Creates pytest test cases for uncovered functions
3. **Issue Prioritizer** → Ranks issues by severity (Critical/High/Medium/Low)
4. **Report Writer** → Compiles comprehensive markdown report with all findings

> **The one rule: THE LOOP NEVER CHANGES. THE TOOLS DO.**
    """)

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Get your free key at console.groq.com",
    )
    st.markdown("[🔑 Get your free Groq API key](https://console.groq.com)")

    st.divider()

    st.markdown("### 🏗️ How Autonomy Works Here")
    st.markdown("""
    **The 5-step loop** (`agent/loop.py`):
    ```
    THINK → PLAN → EXECUTE → REVIEW → UPDATE
      ↑                                  |
      └──────── (if score < 7) ──────────┘
    ```

    **What each file does:**
    - `loop.py` — Runs the 5-step cycle (NEVER changes)
    - `planner.py` — LLM → JSON action plan
    - `executor.py` — Routes plan → tool functions
    - `reviewer.py` — Scores report quality
    - `tools/` — The domain-specific work (THESE change)

    **The 4 tools in this agent:**
    1. `code_scanner` — Finds bugs and issues
    2. `test_case_generator` — Creates test cases
    3. `issue_prioritizer` — Ranks by severity
    4. `report_writer` — Compiles final report

    **Why this is autonomous:**
    The **reviewer** scores the report quality. If the score < 7, it tells the agent *what* to improve — and the agent tries again.
    """)

    st.divider()

    model = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
        help="llama-3.1-8b-instant is fast, llama-3.3-70b-versatile is more capable",
    )

    st.divider()
    st.caption("Built for [StudAI Foundry](https://studai.one) — the national autonomous AI hackathon")

# ── MAIN AREA — INPUT ────────────────────────────────────────────
repo_path = st.text_input(
    "Repository Path",
    value="./mock_repo",
    placeholder="./mock_repo or path to your repository",
    help="Path to the code repository to analyze",
)

# ── RUN BUTTON ───────────────────────────────────────────────────
col_run, col_example = st.columns([3, 1])
with col_run:
    run_button = st.button("🔍 Analyze Code Quality", use_container_width=True, type="primary")
with col_example:
    if st.button("💡 Use Example", use_container_width=True):
        st.session_state["example_repo"] = "./mock_repo"
        st.rerun()

if "example_repo" in st.session_state:
    repo_path = st.session_state.pop("example_repo")

st.divider()

# ── STEP DISPLAY CONTAINERS ─────────────────────────────────────
step_container = st.container()
loop_label = st.empty()
log_header = st.empty()
log_container = st.empty()

# ── STEP ICONS AND LABELS ───────────────────────────────────────
STEP_ICONS = {
    "pending": "○",
    "active": "⚙",
    "done": "✔",
    "failed": "✖",
    "skipped": "↩",
}

STEP_LABELS = ["THINK", "PLAN", "EXECUTE", "REVIEW", "UPDATE"]
STEP_KEYS = ["think", "plan", "execute", "review", "update"]

STEP_DESCRIPTIONS = {
    "think": "Parse repo",
    "plan": "Create plan",
    "execute": "Run tools",
    "review": "Score report",
    "update": "Self-correct",
}


def render_steps(statuses, container):
    """Render the 5 step cards with current statuses."""
    with container:
        container.empty()
        cols = st.columns(5)
        for i, col in enumerate(cols):
            key = STEP_KEYS[i]
            status = statuses.get(key, "pending")
            icon = STEP_ICONS.get(status, "○")
            label = STEP_LABELS[i]
            desc = STEP_DESCRIPTIONS.get(key, "")
            col.markdown(
                f"""<div class="step-card step-{status}">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="font-weight: bold; margin-top: 4px;">{label}</div>
                    <div style="font-size: 11px; margin-top: 2px; opacity: 0.8;">{desc}</div>
                    <div style="font-size: 12px; margin-top: 4px;">{status.upper()}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def format_log(message):
    """Add timestamp and color-code log lines for readability."""
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    time_span = f'<span class="log-time">[{ts}]</span>'

    if message.startswith("═══"):
        return f'{time_span} <span class="log-loop">{message}</span>'
    elif "Running tool:" in message:
        return f'{time_span} <span class="log-tool">{message}</span>'
    elif "PASSED" in message or (
        "passed" in message.lower() and "success" in message.lower()
    ):
        return f'{time_span} <span class="log-pass">{message}</span>'
    elif "FAILED" in message or "failed" in message.lower():
        return f'{time_span} <span class="log-fail">{message}</span>'
    else:
        return f"{time_span} {message}"


# ── RUN THE AGENT ────────────────────────────────────────────────
if run_button:
    # ── VALIDATION ───────────────────────────────────────────────
    if not api_key or "your_groq" in api_key:
        st.error(
            "⚠️ **Groq API key missing.** Paste your key in the sidebar.\n\n"
            "Get one free (no credit card) → [console.groq.com](https://console.groq.com)"
        )
        st.stop()

    if not repo_path.strip():
        st.error(
            "⚠️ **No repository path entered.** Enter a path above, or click **💡 Use Example** for a demo."
        )
        st.stop()

    if not os.path.exists(repo_path):
        st.error(
            f"⚠️ **Repository not found:** `{repo_path}`\n\n"
            "Make sure the path is correct and the repository exists."
        )
        st.stop()

    # ── INITIALISE STATE ─────────────────────────────────────────
    client = Groq(api_key=api_key)
    statuses = {key: "pending" for key in STEP_KEYS}
    log_lines = []
    current_loop = [1]

    render_steps(statuses, step_container)
    log_header.markdown("### 📋 Activity Log")

    # ── CALLBACKS ────────────────────────────────────────────────
    def on_step(step, status):
        """Update a step card status and re-render all cards."""
        statuses[step] = status
        render_steps(statuses, step_container)

    def on_log(message):
        """Append a timestamped log line and re-render the log box."""
        if message.startswith("═══ Loop"):
            try:
                loop_num = int(message.split("Loop ")[1].split(" ")[0])
                current_loop[0] = loop_num
                max_loops = int(message.split("of ")[1].split(" ")[0])
                loop_label.markdown(
                    f'<div class="loop-counter">AUTONOMOUS LOOP: {loop_num} of {max_loops}</div>',
                    unsafe_allow_html=True,
                )
            except (ValueError, IndexError):
                pass

        log_lines.append(format_log(message))
        visible = log_lines[-12:]
        log_html = "\n".join(visible)
        log_container.markdown(
            f'<div class="log-box">{log_html}</div>',
            unsafe_allow_html=True,
        )

    # ── RUN THE LOOP ─────────────────────────────────────────────
    with st.spinner("🤖 Agent is analyzing code quality autonomously — watch the steps light up..."):
        try:
            results = loop.run(repo_path, client, model, on_step, on_log)
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                st.error(
                    "🔑 **API key error.** Your Groq key may be invalid or expired.\n\n"
                    "Get a new one → [console.groq.com](https://console.groq.com)"
                )
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                st.error(
                    "⏳ **Rate limited by Groq.** You've hit the free tier limit.\n\n"
                    "Wait 60 seconds and try again, or switch to a smaller model in the sidebar."
                )
            elif "model" in error_msg.lower():
                st.error(
                    f"🧠 **Model error.** The selected model may be unavailable.\n\n"
                    f"Try a different model from the sidebar.\n\nDetails: `{error_msg}`"
                )
            else:
                st.error(
                    f"❌ **Agent error:** `{error_msg}`\n\nCheck your API key and internet connection."
                )
            st.stop()

    # ── DISPLAY RESULTS ──────────────────────────────────────────
    st.divider()

    st.markdown("## 📊 Code Quality Analysis Report")

    if results.get("report_writer"):
        report = results["report_writer"]
        scanner_output = results.get("code_scanner", "")
        test_output = results.get("test_case_generator", "")
        priority_output = results.get("issue_prioritizer", "")

        # Parse scanner summary
        try:
            scanner_data = json.loads(scanner_output)
            summary = scanner_data.get("summary", {})
        except:
            summary = {}

        # ── TABBED VIEW ──────────────────────────────────────────
        tab_summary, tab_tests, tab_report, tab_reasoning = st.tabs(
            ["📊 Issue Summary", "🧪 Generated Tests", "📄 Full Report", "🧠 Agent Reasoning"]
        )

        # ── TAB 1: ISSUE SUMMARY ──────────────────────────────────
        with tab_summary:
            st.markdown("### Issues Found")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Critical", summary.get("critical", 0), delta=None, delta_color="inverse")
            with col2:
                st.metric("High", summary.get("high", 0), delta=None, delta_color="inverse")
            with col3:
                st.metric("Medium", summary.get("medium", 0))
            with col4:
                st.metric("Low", summary.get("low", 0))

            st.markdown(f"**Total Issues:** {summary.get('total_issues', 0)} across {summary.get('files_analyzed', 0)} files")

            st.divider()

            # Show prioritized issues
            try:
                priority_data = json.loads(priority_output)
                
                if priority_data.get("critical"):
                    st.markdown("### ⚠️ Critical Issues")
                    for issue in priority_data["critical"]:
                        with st.expander(f"🔴 {issue.get('file', 'Unknown')} - {issue.get('issue', 'No description')}"):
                            st.markdown(f"**Impact:** {issue.get('impact', 'N/A')}")
                            st.markdown(f"**Effort:** {issue.get('effort', 'N/A')}")

                if priority_data.get("high"):
                    st.markdown("### 🔶 High Priority Issues")
                    for issue in priority_data["high"][:5]:  # Show top 5
                        with st.expander(f"🟠 {issue.get('file', 'Unknown')} - {issue.get('issue', 'No description')}"):
                            st.markdown(f"**Impact:** {issue.get('impact', 'N/A')}")
                            st.markdown(f"**Effort:** {issue.get('effort', 'N/A')}")

                if priority_data.get("recommendations"):
                    st.markdown("### 💡 Recommendations")
                    for rec in priority_data["recommendations"]:
                        st.info(rec)
            except:
                st.warning("Could not parse prioritized issues")

        # ── TAB 2: GENERATED TESTS ────────────────────────────────
        with tab_tests:
            st.markdown("### Generated Test Cases")
            st.markdown("Copy-paste these pytest test cases into your test files:")
            st.code(test_output, language="python")
            
            st.download_button(
                label="📥 Download Test Cases",
                data=test_output,
                file_name="generated_tests.py",
                mime="text/x-python",
                use_container_width=True,
            )

        # ── TAB 3: FULL REPORT ────────────────────────────────────
        with tab_report:
            st.markdown(report)
            st.divider()
            st.download_button(
                label="📥 Download Full Report",
                data=report,
                file_name="code_quality_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ── TAB 4: AGENT REASONING ────────────────────────────────
        with tab_reasoning:
            st.markdown("### 🧠 How the Agent Analyzed Your Code")

            # Tool pipeline visualization
            st.markdown("**4-Tool Pipeline:**")
            p_cols = st.columns(4)
            pipeline_tools = [
                ("1️⃣", "Code\nScanner", "Find Issues"),
                ("2️⃣", "Test\nGenerator", "Create Tests"),
                ("3️⃣", "Issue\nPrioritizer", "Rank Severity"),
                ("4️⃣", "Report\nWriter", "Compile Report"),
            ]
            for i, col in enumerate(p_cols):
                icon, name, output = pipeline_tools[i]
                col.markdown(
                    f"""<div class="pipeline-card">
                        <div style="font-size: 24px;">{icon}</div>
                        <div style="font-weight: bold; margin-top: 4px;">{name}</div>
                        <div style="font-size: 11px; color: #666; margin-top: 4px;">{output}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # Loops used
            loops_used = current_loop[0]
            st.markdown(f"**Autonomous loops used:** {loops_used} of 3")
            if loops_used == 1:
                st.success("Report passed quality review on the first attempt!")
            else:
                st.info(
                    f"The agent self-corrected {loops_used - 1} time(s) based on reviewer feedback."
                )

            st.markdown("---")

            st.markdown("### 📝 Raw Tool Outputs")
            with st.expander("Code Scanner Output"):
                st.json(scanner_output)
            with st.expander("Test Generator Output"):
                st.code(test_output, language="python")
            with st.expander("Issue Prioritizer Output"):
                st.json(priority_output)

    else:
        st.warning("No report was generated. Check the activity log above for errors.")

    # ── POST-RUN EDUCATION ───────────────────────────────────────
    with st.expander("🎓 What just happened? (The autonomy explained)"):
        loops_used = current_loop[0]
        st.markdown(f"""
**The agent ran {loops_used} loop{'s' if loops_used > 1 else ''}** to analyze your code. Here's what happened:

1. **THINK** — The agent parsed the repository path. On retries, it incorporated reviewer feedback about report quality.

2. **PLAN** — The agent created a JSON plan: run code_scanner → test_case_generator → issue_prioritizer → report_writer. It decided this order itself.

3. **EXECUTE** — The agent ran **4 tools** in sequence. Each builds on the previous:
   - **Code Scanner** → Found bugs, complexity issues, security vulnerabilities
   - **Test Case Generator** → Created pytest test cases for uncovered functions
   - **Issue Prioritizer** → Ranked issues by severity (Critical/High/Medium/Low)
   - **Report Writer** → Compiled comprehensive markdown report

4. **REVIEW** — The agent scored the report quality on 5 aspects: issue detection, test coverage, prioritization, report quality, and completeness.

5. **UPDATE** — If overall score < 7, the agent carried specific feedback into the next loop.

**This is the same 5-step loop used in production AI agents. The domain changes (code quality vs. customer support vs. invoice processing), but the loop stays the same.**
        """)