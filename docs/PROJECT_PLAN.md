# AI-Powered Autonomous Code Quality Monitor

## Project Overview

An autonomous AI agent that monitors code quality, detects bugs, generates test cases, and creates structured issue reports without manual intervention. Built on the StudAI Foundry LaunchPad template architecture.

---

## Core Innovation: The Autonomous Loop

Unlike traditional static analysis tools, this system uses a **5-step autonomous loop**:

```
THINK → PLAN → EXECUTE → REVIEW → UPDATE
  ↑                                  ↓
  └──────── (if score < 7) ──────────┘
```

**What makes it autonomous:**
- **Self-planning**: Agent decides its own workflow
- **Self-execution**: Runs multiple tools in sequence
- **Self-review**: Evaluates its own output quality (1-10 score)
- **Self-correction**: Retries with specific improvements if quality is low

---

## Architecture

### The Universal Loop (Never Changes)

```
agent/loop.py
├── THINK  → Parse goal + incorporate feedback
├── PLAN   → LLM creates JSON action plan
├── EXECUTE → Run tools in sequence
├── REVIEW → Score output against criteria
└── UPDATE → Carry feedback to next iteration
```

### Domain-Specific Tools (These Change)

```
agent/tools/
├── code_scanner.py         → Detects bugs, complexity, vulnerabilities
├── test_case_generator.py  → Generates pytest test cases
├── issue_prioritizer.py    → Ranks issues by severity
└── report_writer.py        → Compiles structured report
```

### Information Chaining

```
code_scanner
    ↓ (issues found)
test_case_generator
    ↓ (test cases + issues)
issue_prioritizer
    ↓ (prioritized issues + tests)
report_writer
    ↓ (final report)
```

---

## Technology Stack

### MVP (Days 1-2) ✅

| Technology | Purpose | Status |
|------------|---------|--------|
| **Groq API** | LLM for code understanding (Llama 3.3 70B) | ✅ In template |
| **Python 3.10+** | Backend orchestration | ✅ In template |
| **Streamlit** | Rapid UI prototyping | ✅ In template |
| **Mock Data** | Sample repositories with intentional bugs | 🔨 To create |

### Post-MVP Enhancements (Days 3-10) 🔄

| Technology | Purpose | Timeline |
|------------|---------|----------|
| **FAISS** | Vector database for code embeddings | Days 3-5 |
| **sentence-transformers** | Generate code embeddings | Days 3-5 |
| **PyGithub** | Real repository monitoring | Days 4-6 |
| **Jira API** | Automatic ticket creation | Days 5-7 |
| **FastAPI** | Webhook handling + API endpoints | Days 6-8 |
| **React** | Production dashboard | Days 7-10 |

---

## Implementation Phases

### Phase 1: MVP (Days 1-2) - Core Autonomy

**Goal**: Prove the autonomous agent architecture works

**Deliverables**:
- ✅ 4 code quality analysis tools
- ✅ 5-step autonomous loop with self-review
- ✅ Button-triggered analysis (manual)
- ✅ Mock repository with intentional bugs
- ✅ Streamlit UI showing results
- ✅ Demo video

**Day 1 Tasks** (6-8 hours):
1. Create mock repository with code issues
2. Implement `code_scanner.py`
3. Implement `test_case_generator.py`
4. Implement `issue_prioritizer.py`
5. Implement `report_writer.py`
6. Update `planner.py` AVAILABLE_TOOLS
7. Update `executor.py` tool routing

**Day 2 Tasks** (6-8 hours):
8. Update `reviewer.py` scoring criteria
9. Modify `main.py` UI for code quality reports
10. Test full autonomous loop
11. Fix bugs and improve prompts
12. Create demo video
13. Write documentation

**Success Criteria**:
- Agent runs end-to-end without manual intervention
- Finds at least 5 different types of code issues
- Generates at least 3 test cases
- Produces structured report with severity levels
- Self-reviews and retries if quality < 7/10
- Demo-ready for CP2

---

### Phase 2: RAG Integration (Days 3-5)

**Goal**: Add contextual code analysis using vector embeddings

**New Dependencies**:
```bash
pip install faiss-cpu sentence-transformers
```

**New Tool**: `code_similarity_finder.py`
- Stores code embeddings in FAISS
- Finds similar code patterns across repository
- Enhances `code_scanner` with contextual insights

**Integration**:
```python
# In code_scanner.py
similar_code = code_similarity_finder.find_similar(function_code)
# Use similar code patterns to improve bug detection
```

---

### Phase 3: GitHub API Integration (Days 4-6)

**Goal**: Monitor real repositories and analyze actual commits

**New Dependencies**:
```bash
pip install PyGithub
```

**New Features**:
- Real repository monitoring
- Fetch code changes from commits
- Post review comments on pull requests
- Track repository activity

**Implementation**:
```python
# github_monitor.py
from github import Github

def fetch_latest_commit(repo_url):
    g = Github(api_key)
    repo = g.get_repo(repo_url)
    commit = repo.get_commits()[0]
    return commit.files
```

---

### Phase 4: Jira Integration (Days 5-7)

**Goal**: Automatically create tickets for detected issues

**New Dependencies**:
```bash
pip install jira
```

**New Features**:
- Automatic ticket creation
- Task assignment based on file ownership
- Status tracking
- Link tickets to GitHub issues

**Implementation**:
```python
# jira_integration.py
from jira import JIRA

def create_bug_ticket(issue_details):
    jira = JIRA(server, auth=(email, api_token))
    ticket = jira.create_issue(
        project='PROJ',
        summary=issue_details['title'],
        description=issue_details['description'],
        issuetype={'name': 'Bug'}
    )
    return ticket.key
```

---

### Phase 5: FastAPI Backend (Days 6-8)

**Goal**: Add webhook support for automatic triggers

**New Dependencies**:
```bash
pip install fastapi uvicorn
```

**New Features**:
- GitHub webhook endpoint
- Background task processing
- API for React frontend
- Real-time monitoring

**Implementation**:
```python
# webhook_server.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/github")
async def handle_push(request: Request):
    payload = await request.json()
    if payload['event'] == 'push':
        # Trigger autonomous agent
        agent.run(payload['commits'])
```

---

### Phase 6: React Dashboard (Days 7-10)

**Goal**: Production-grade visualization and interaction

**Setup**:
```bash
npx create-react-app dashboard
cd dashboard
npm install axios recharts
```

**Features**:
- Real-time monitoring dashboard
- Interactive charts (issues over time, test coverage)
- Code quality metrics
- Developer leaderboard
- Better UX than Streamlit

---

## MVP Demo Flow

### User Experience

1. **User clicks "Analyze Code Quality" button**
2. **Agent shows 5 step cards lighting up in real-time**:
   - THINK → "Parsing repository structure..."
   - PLAN → "Planning: scan → test → prioritize → report"
   - EXECUTE → "Running code_scanner... test_case_generator... issue_prioritizer... report_writer..."
   - REVIEW → "Scoring report quality: 8/10 - PASSED"
   - UPDATE → [Skipped if passed, or "Retrying with improvements..."]
3. **Results displayed in 4 tabs**:
   - **Tab 1**: Issue Summary (by severity)
   - **Tab 2**: Generated Test Cases (copy-paste ready)
   - **Tab 3**: Full Report (markdown)
   - **Tab 4**: Agent Reasoning (what it found and why)

### Demo Script for CP2

```
"Hi, I'm demonstrating our autonomous code quality agent.

[Click 'Analyze Code Quality' button]

Watch the 5 steps light up in real-time. The agent is:
- THINKING: Parsing the repository
- PLANNING: Deciding to scan → test → prioritize → report
- EXECUTING: Running all 4 tools in sequence
- REVIEWING: Scoring its own report quality
- [If needed] UPDATING: Retrying with improvements

[Results appear]

Here's what the agent found autonomously:
- 5 code quality issues (2 critical, 3 medium)
- Generated 3 test cases for uncovered functions
- Prioritized action items by severity
- Structured report ready for the team

The key innovation: The agent REVIEWS its own work.
If the report quality is below 7/10, it automatically
retries with specific improvements. No human intervention needed.

This is the same 5-step loop used in production AI agents.
The domain changes, but the autonomy architecture stays the same."
```

---

## File Structure

```
studai-foundry-launchpad/
│
├── PROJECT_PLAN.md              ← This file
├── MVP_IMPLEMENTATION.md        ← Detailed implementation guide
├── README.md                    ← Updated for code quality monitor
├── requirements.txt             ← Dependencies
├── .env.example                 ← API key template
│
├── main.py                      ← Streamlit UI (modified for code quality)
│
├── agent/
│   ├── loop.py                  ← THE CORE (never changes)
│   ├── planner.py               ← Updated AVAILABLE_TOOLS
│   ├── executor.py              ← Updated tool routing
│   ├── reviewer.py              ← Updated scoring criteria
│   │
│   └── tools/
│       ├── code_scanner.py      ← NEW: Detects bugs and issues
│       ├── test_case_generator.py ← NEW: Generates test cases
│       ├── issue_prioritizer.py ← NEW: Ranks by severity
│       └── report_writer.py     ← NEW: Compiles final report
│
└── mock_repo/                   ← Sample code with intentional bugs
    ├── src/
    │   ├── main.py
    │   ├── utils.py
    │   └── api.py
    └── tests/
        └── test_utils.py
```

---

## CP1 Submission Content

### Field 1: Problem Statement

The AI agent solves the problem of manual code review, bug detection, and test validation faced by mid-sized to large software development teams in India, particularly those in tech hubs like Bengaluru, Hyderabad, and Pune. These teams experience significant delays and quality issues due to the manual effort required, resulting in bottlenecks, increased release time, and critical bugs reaching production. The current approach is not only time-consuming but also prone to human error, making it essential to develop an AI-powered solution to address this problem.

### Field 2: Target Users

Mid-sized to large software development teams in India, including e-commerce companies, fintech startups, and IT service providers like Infosys, Wipro, and TCS, as well as product-based startups like Flipkart and Paytm.

### Field 3: Autonomy Loop Plan

The AI agent operates autonomously using a 5-step loop:
- **THINK**: Parses the code repository structure and identifies files to analyze
- **PLAN**: Creates a JSON action plan to scan code → generate tests → prioritize issues → compile report
- **EXECUTE**: Runs 4 specialized tools in sequence (code_scanner, test_case_generator, issue_prioritizer, report_writer), with each tool building on the previous output
- **REVIEW**: Scores the report quality on a 1-10 scale, checking for issue coverage, test case effectiveness, and report completeness
- **UPDATE**: If score < 7, carries specific feedback (e.g., "add more test cases for edge cases") into the next loop iteration

### Field 4: Tools & APIs

Groq API (Llama 3.3 70B), Python, Streamlit, python-dotenv, PyGithub (planned), Jira API (planned), FAISS (planned), sentence-transformers (planned), FastAPI (planned), React (planned)

### Field 5: Evaluation Logic

The agent's output is considered successful if it meets quality criteria such as:
- Code review coverage of at least 90% of modified files
- Test case effectiveness of at least 80% (tests cover critical functions)
- Issue detection accuracy of at least 95% (low false positive rate)
- Report completeness score of at least 7/10 from the self-review step

### Field 6: Expected Output

A comprehensive code quality report including:
- Identified defects with severity levels (Critical/High/Medium/Low)
- Generated test cases in pytest format (copy-paste ready)
- Prioritized action items for developers
- Structured markdown report with executive summary
- [Future] Automatically created Jira tickets with issue details

---

## Success Metrics

### MVP Success (CP2 Demo)
- ✅ Agent completes full autonomous loop
- ✅ Finds 5+ code quality issues
- ✅ Generates 3+ test cases
- ✅ Self-reviews and passes quality check
- ✅ Demo runs smoothly in 3-5 minutes

### Final Product Success (CP3)
- ✅ All MVP features working
- ✅ At least 2 post-MVP features integrated (RAG, GitHub, or Jira)
- ✅ Production-ready documentation
- ✅ Clear roadmap for remaining features

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|------------|
| LLM API rate limits | Use Groq free tier (14,400 req/day), implement retry logic |
| Poor code analysis quality | Iterate on prompts, add examples to tool prompts |
| Self-review too lenient/strict | Tune PASS_THRESHOLD, adjust scoring criteria |
| Integration complexity | Build MVP first, add integrations incrementally |

### Timeline Risks

| Risk | Mitigation |
|------|------------|
| MVP takes longer than 2 days | Focus on 3 tools instead of 4, simplify UI |
| Post-MVP features delayed | Prioritize: RAG → GitHub → Jira → FastAPI → React |
| Demo breaks during presentation | Record backup video, test thoroughly |

---

## Next Steps

1. ✅ Document project plan (this file)
2. 🔨 Create detailed implementation guide
3. 🔨 Start MVP implementation (Day 1)
4. 🔨 Complete MVP (Day 2)
5. 🔨 Add post-MVP features (Days 3-10)
6. 🔨 Prepare final submission

---

## References

- StudAI Foundry: https://studai.one
- Template Repository: https://github.com/studaiedutech-ui/studai-foundry-launchpad
- Groq API: https://console.groq.com
- Hackathon Timeline: March 19-30, 2026