# ============================================================
# main.py — Streamlit UI for Code Quality Monitor (Phase 4)
# ============================================================
# PHASE 4 FEATURES:
#   - GitHub repository input (required)
#   - File selection with checkboxes
#   - Pagination (20 files per page)
#   - Search & filter
#   - Smart changed file detection
#   - Per-file analysis results
#   - Commit SHA tracking
# ============================================================

import os
import datetime
import json
import tempfile
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from agent import loop
from agent.tools import github_integration
from utils import CommitTracker

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
</style>
""", unsafe_allow_html=True)

# ── INITIALIZE SESSION STATE ────────────────────────────────────
if 'repo_files' not in st.session_state:
    st.session_state.repo_files = []
if 'changed_files' not in st.session_state:
    st.session_state.changed_files = []
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []
if 'current_commit' not in st.session_state:
    st.session_state.current_commit = None
if 'repo_url' not in st.session_state:
    st.session_state.repo_url = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# ── HEADER & BRANDING ───────────────────────────────────────────
st.markdown('<div class="brand-title">Code Quality Monitor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-sub">Autonomous AI Agent for Code Analysis</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="brand-badge"><span>STUDAI FOUNDRY — PHASE 4: GITHUB INTEGRATION</span></div>',
    unsafe_allow_html=True,
)

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔐 API Configuration")

    groq_api_key = st.text_input(
        "Groq API Key *",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Required: Get your free key at console.groq.com",
    )
    
    github_token = st.text_input(
        "GitHub Token *",
        type="password",
        value=os.getenv("GITHUB_TOKEN", ""),
        help="Required: Get token from github.com/settings/tokens",
    )
    
    if not groq_api_key or not github_token:
        st.warning("⚠️ Both API keys are required")
    
    st.markdown("[🔑 Get Groq API key](https://console.groq.com)")
    st.markdown("[🔑 Get GitHub token](https://github.com/settings/tokens)")

    st.divider()

    model = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
        help="llama-3.1-8b-instant is fast, llama-3.3-70b-versatile is more capable",
    )

    st.divider()
    
    st.markdown("### 📊 Repository Stats")
    if st.session_state.repo_files:
        st.metric("Total Files", len(st.session_state.repo_files))
        st.metric("Changed Files", len(st.session_state.changed_files))
        st.metric("Selected", len(st.session_state.selected_files))

# ── MAIN AREA — GITHUB INPUT ────────────────────────────────────
st.markdown("## 📦 Step 1: Fetch Repository")

repo_url = st.text_input(
    "GitHub Repository URL *",
    value=st.session_state.repo_url,
    placeholder="https://github.com/owner/repo",
    help="Enter the full GitHub repository URL",
)

col1, col2 = st.columns([3, 1])
with col1:
    fetch_button = st.button("🔍 Fetch Repository", use_container_width=True, type="primary")
with col2:
    if st.button("💡 Use Example", use_container_width=True):
        st.session_state.repo_url = "https://github.com/Kaushik-SPACEZ/github-agent"
        st.rerun()

# ── FETCH REPOSITORY ────────────────────────────────────────────
if fetch_button:
    if not groq_api_key or not github_token:
        st.error("⚠️ Both Groq API key and GitHub token are required!")
        st.stop()
    
    if not repo_url.strip():
        st.error("⚠️ Please enter a GitHub repository URL")
        st.stop()
    
    with st.spinner("🔍 Fetching repository from GitHub..."):
        try:
            # Initialize commit tracker
            tracker = CommitTracker()
            
            # Get latest commit
            commit_result = github_integration.get_latest_commit_sha(repo_url, github_token)
            if not commit_result['success']:
                st.error(f"❌ Error: {commit_result['error']}")
                st.stop()
            
            current_commit = commit_result['sha']
            
            # Check if first analysis
            is_first = tracker.is_first_analysis(repo_url)
            
            # Fetch all files
            files_result = github_integration.list_all_code_files(repo_url, github_token)
            if not files_result['success']:
                st.error(f"❌ Error: {files_result['error']}")
                st.stop()
            
            all_files = files_result['files']
            
            # Determine changed files
            changed_files = []
            if not is_first:
                last_commit = tracker.get_last_commit(repo_url)
                if last_commit:
                    changes_result = github_integration.get_changed_files_between_commits(
                        repo_url, last_commit, current_commit, github_token
                    )
                    if changes_result['success']:
                        changed_files = [f['path'] for f in changes_result['modified']]
            
            # Store in session state
            st.session_state.repo_files = all_files
            st.session_state.changed_files = changed_files
            st.session_state.selected_files = changed_files.copy()  # Auto-select changed
            st.session_state.current_commit = current_commit
            st.session_state.repo_url = repo_url
            st.session_state.current_page = 1
            
            # Show success message
            if is_first:
                st.success(f"✅ First analysis! Fetched {len(all_files)} files from {files_result['repo_name']}")
            else:
                st.success(f"✅ Fetched {len(all_files)} files. {len(changed_files)} files changed since last analysis.")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error fetching repository: {str(e)}")
            st.stop()

# ── FILE SELECTION UI ───────────────────────────────────────────
if st.session_state.repo_files:
    st.divider()
    st.markdown("## 📁 Step 2: Select Files to Analyze")
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Search files", placeholder="e.g., main.py")
    with col2:
        file_extensions = list(set([f['extension'] for f in st.session_state.repo_files]))
        file_type_filter = st.multiselect("Filter by type", options=file_extensions)
    
    # Filter files
    filtered_files = st.session_state.repo_files
    if search_query:
        filtered_files = [f for f in filtered_files if search_query.lower() in f['path'].lower()]
    if file_type_filter:
        filtered_files = [f for f in filtered_files if f['extension'] in file_type_filter]
    
    # Pagination
    items_per_page = 20
    total_files = len(filtered_files)
    total_pages = max(1, (total_files + items_per_page - 1) // items_per_page)
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✅ Select All", use_container_width=True):
            st.session_state.selected_files = [f['path'] for f in filtered_files]
            st.rerun()
    with col2:
        if st.button("🔴 Select Changed Only", use_container_width=True):
            st.session_state.selected_files = st.session_state.changed_files.copy()
            st.rerun()
    with col3:
        if st.button("❌ Clear Selection", use_container_width=True):
            st.session_state.selected_files = []
            st.rerun()
    with col4:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=st.session_state.current_page, label_visibility="collapsed")
        st.session_state.current_page = page
    
    # Calculate page range
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_files)
    page_files = filtered_files[start_idx:end_idx]
    
    st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_files} files (Page {page}/{total_pages})")
    
    # File checkboxes
    for file in page_files:
        is_changed = file['path'] in st.session_state.changed_files
        is_selected = file['path'] in st.session_state.selected_files
        
        # Create label with badge
        badge = " 🔴 **Modified**" if is_changed else ""
        label = f"`{file['path']}`{badge} ({file['size']} bytes)"
        
        # Checkbox
        checked = st.checkbox(
            label,
            value=is_selected,
            key=f"file_{file['path']}_{page}"
        )
        
        # Update selection
        if checked and file['path'] not in st.session_state.selected_files:
            st.session_state.selected_files.append(file['path'])
        elif not checked and file['path'] in st.session_state.selected_files:
            st.session_state.selected_files.remove(file['path'])
    
    # Analysis button
    st.divider()
    if len(st.session_state.selected_files) > 0:
        analyze_button = st.button(
            f"🚀 Analyze {len(st.session_state.selected_files)} Selected Files",
            use_container_width=True,
            type="primary"
        )
    else:
        st.warning("⚠️ No files selected. Select at least one file to analyze.")
        analyze_button = False

else:
    analyze_button = False

# ── RUN ANALYSIS ────────────────────────────────────────────────
if analyze_button:
    st.divider()
    st.markdown("## 🤖 Step 3: Running Analysis")
    
    # Create temp directory with selected files
    with st.spinner("📥 Fetching file contents from GitHub..."):
        temp_dir = tempfile.mkdtemp(prefix='github_analysis_')
        
        try:
            for file_path in st.session_state.selected_files:
                content_result = github_integration.fetch_file_content(
                    st.session_state.repo_url,
                    file_path,
                    st.session_state.current_commit,
                    github_token
                )
                
                if content_result['success']:
                    full_path = os.path.join(temp_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content_result['content'])
            
            st.success(f"✅ Fetched {len(st.session_state.selected_files)} files")
            
            # Run analysis
            st.markdown("### 🔄 Autonomous Agent Running...")
            
            client = Groq(api_key=groq_api_key)
            
            # Simplified display for now
            with st.spinner("🤖 Analyzing code quality..."):
                results = loop.run(temp_dir, client, model, lambda s, st: None, lambda m: None)
            
            # Save commit SHA
            tracker = CommitTracker()
            tracker.save_commit(
                st.session_state.repo_url,
                st.session_state.current_commit,
                st.session_state.selected_files
            )
            
            # Display results
            st.divider()
            st.markdown("## 📊 Analysis Results")
            
            if results.get("report_writer"):
                st.markdown(results["report_writer"])
                
                st.download_button(
                    label="📥 Download Report",
                    data=results["report_writer"],
                    file_name="code_quality_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            else:
                st.warning("No report generated")
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)