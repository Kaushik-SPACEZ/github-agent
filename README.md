# 🔍 Code Quality Monitor — Autonomous AI Agent - very good

> **Built on StudAI Foundry LaunchPad** — Demonstrates autonomous agent architecture for code quality analysis

An autonomous AI agent that analyzes code repositories, detects bugs, generates test cases, and creates comprehensive quality reports **without manual intervention**.

```
  ╔═══════════════════════════════════════════════════════════════════╗
  ║                                                                   ║
  ║      🔍 CODE QUALITY MONITOR                                      ║
  ║      Autonomous AI Agent for Code Analysis                        ║
  ║                                                                   ║
  ║      THINK → PLAN → EXECUTE → REVIEW → UPDATE                     ║
  ║        ↑                                  ↓                       ║
  ║        └──────── (if score < 7) ──────────┘                       ║
  ║                                                                   ║
  ╚═══════════════════════════════════════════════════════════════════╝
```

---

## 🎯 What Makes This Autonomous?

**A chatbot** takes input → calls LLM → returns output. One shot. Done.

**An autonomous agent** takes a goal and then:
1. **THINKS** about the goal + any feedback from previous attempts
2. **PLANS** what tools to use (it decides, not you)
3. **EXECUTES** tools in sequence with information chaining
4. **REVIEWS** its own output quality (scores 1-10)
5. **UPDATES** with specific feedback and retries if needed

**The loop runs up to 3 times.** Each retry uses specific feedback to improve.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API key (free, no credit card) → [console.groq.com](https://console.groq.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/studaiedutech-ui/studai-foundry-launchpad.git
cd studai-foundry-launchpad

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add your Groq API key

# Run the app
streamlit run main.py
```

The app opens at **http://localhost:8501**

---

## 💻 Usage

1. **Paste your Groq API key** in the sidebar (or set in `.env`)
2. **Enter repository path** (default: `./mock_repo`)
3. **Click "🔍 Analyze Code Quality"**
4. **Watch the 5 steps light up** in real-time
5. **View results** in 4 tabs:
   - **Issue Summary** — Critical/High/Medium/Low breakdown
   - **Generated Tests** — Copy-paste ready pytest code
   - **Full Report** — Comprehensive markdown report
   - **Agent Reasoning** — See how the agent thought

---

## 🏗️ Architecture

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
code_scanner (finds issues)
    ↓
test_case_generator (creates tests for issues)
    ↓
issue_prioritizer (ranks by severity)
    ↓
report_writer (compiles everything)
```

---

## 🔧 What the Agent Does

### 1. Code Scanner
- Detects high complexity functions (>10 branches)
- Finds missing error handling
- Identifies security vulnerabilities (hardcoded credentials, SQL injection, eval())
- Detects code duplication
- Finds missing docstrings
- Flags functions without tests

### 2. Test Case Generator
- Identifies functions lacking test coverage
- Generates pytest test cases for:
  - Normal/happy path
  - Edge cases (empty inputs, None, invalid types)
  - Error conditions
- Produces copy-paste ready Python code

### 3. Issue Prioritizer
- Ranks issues into 4 categories:
  - **CRITICAL**: Security vulnerabilities, data loss risks
  - **HIGH**: Bugs affecting core functionality
  - **MEDIUM**: Code quality issues, missing tests
  - **LOW**: Style issues, minor improvements
- Provides fix effort estimates (quick/medium/large)
- Generates actionable recommendations

### 4. Report Writer
- Compiles comprehensive markdown report with:
  - Executive summary
  - Issue breakdown by severity
  - Generated test cases
  - Recommended actions
  - Mock Jira tickets (what would be created)

---

## 📊 Example Output

```
Code Quality Analysis Report

Executive Summary
- Total issues: 15
- Critical: 3 (hardcoded credentials, SQL injection, eval() usage)
- High: 5 (missing error handling, high complexity)
- Medium: 4 (code duplication, missing docstrings)
- Low: 3 (style issues)
- Files analyzed: 3

Critical Issues ⚠️
1. main.py:10 - Hardcoded database password 'admin123'
   Impact: Security breach risk
   Fix: Use environment variables

2. main.py:25 - SQL injection vulnerability
   Impact: Database compromise possible
   Fix: Use parameterized queries

Generated Test Cases 🧪
[Copy-paste ready pytest code]

Recommended Actions
1. Fix all critical security issues immediately
2. Add error handling to database operations
3. Generate tests for uncovered functions
```

---

## 🎓 How to Extend

### Change the Domain

The loop never changes. The tools do.

**Current**: Code quality monitoring  
**Change to**: Customer support, invoice processing, sales qualification, etc.

```python
# Keep loop.py exactly the same
# Change files in agent/tools/

# Example: Customer Support Agent
agent/tools/
├── ticket_classifier.py    → Classify support tickets
├── knowledge_search.py     → Search knowledge base
├── tone_checker.py         → Verify professional tone
└── response_drafter.py     → Draft customer response
```

### Add a New Tool

1. Create `agent/tools/your_tool.py` with a `run()` function
2. Add to `AVAILABLE_TOOLS` in `agent/planner.py`
3. Add routing in `agent/executor.py`
4. Update review criteria in `agent/reviewer.py` if needed

---

## 📁 Project Structure

```
studai-foundry-launchpad/
│
├── PROJECT_PLAN.md              ← Comprehensive project plan
├── MVP_IMPLEMENTATION.md        ← Implementation guide
├── README.md                    ← This file
├── requirements.txt             ← Dependencies (groq, streamlit, python-dotenv)
├── .env.example                 ← API key template
│
├── main.py                      ← Streamlit UI
│
├── agent/
│   ├── loop.py                  ← THE CORE (5-step autonomy loop)
│   ├── planner.py               ← LLM → JSON action plan
│   ├── executor.py              ← Routes plan → tool functions
│   ├── reviewer.py              ← Scores output quality
│   │
│   └── tools/
│       ├── code_scanner.py      ← Detects bugs and issues
│       ├── test_case_generator.py ← Generates test cases
│       ├── issue_prioritizer.py ← Ranks by severity
│       └── report_writer.py     ← Compiles final report
│
└── mock_repo/                   ← Sample code with intentional bugs
    ├── src/
    │   ├── main.py              ← High complexity, security issues
    │   ├── utils.py             ← Code duplication, missing docstrings
    │   └── api.py               ← Security vulnerabilities
    └── tests/
        └── test_utils.py        ← Partial test coverage
```

---

## 🔬 Testing

### Test with Mock Repository

```bash
streamlit run main.py
# Enter: ./mock_repo
# Click: Analyze Code Quality
```

The mock repository contains **15+ intentional issues** across all severity levels.

### Test with Your Own Code

```bash
streamlit run main.py
# Enter: /path/to/your/repository
# Click: Analyze Code Quality
```

---

## ⚙️ Technology Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **LLM Provider** | Groq API | Free tier (14,400 req/day), 300+ tokens/sec |
| **LLM Model** | Llama 3.3 70B | Fast, capable, free |
| **UI Framework** | Streamlit | Zero frontend knowledge needed |
| **Language** | Python 3.10+ | Simple, widely known |
| **Dependencies** | 3 packages only | No bloat |

---

## 📈 Roadmap

### MVP (Complete) ✅
- [x] 4 code quality analysis tools
- [x] 5-step autonomous loop with self-review
- [x] Button-triggered analysis
- [x] Mock repository with intentional bugs
- [x] Streamlit UI

### Post-MVP Enhancements 🔄
- [ ] RAG + FAISS for code similarity search
- [ ] GitHub API for real repository monitoring
- [ ] Jira API for automatic ticket creation
- [ ] FastAPI backend for webhook support
- [ ] React dashboard for production UI

---

## 🤝 Contributing

This project demonstrates autonomous agent architecture. To adapt it:

1. Keep `agent/loop.py` exactly the same
2. Change files in `agent/tools/` for your domain
3. Update `AVAILABLE_TOOLS` in `agent/planner.py`
4. Update routing in `agent/executor.py`
5. Update review criteria in `agent/reviewer.py`

---

## 📝 License

Built for [StudAI Foundry](https://studai.one) — India's national autonomous AI hackathon.

---

## 🎯 Key Takeaway

**THE LOOP NEVER CHANGES. THE TOOLS DO.**

This is the universal pattern for autonomous AI agents. Whether you're building:
- Code quality monitoring
- Customer support automation
- Invoice processing
- Sales lead qualification
- Medical case triage

...you use the exact same 5-step loop. Only the tools change.

---

## 📚 Learn More

- **StudAI Foundry**: https://studai.one
- **Groq API**: https://console.groq.com
- **Streamlit**: https://streamlit.io

---

**Built with ❤️ for StudAI Foundry Hackathon**
