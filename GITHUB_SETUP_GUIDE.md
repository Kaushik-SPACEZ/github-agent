# GitHub Integration Setup Guide

## Overview

This guide explains how to set up automatic code quality analysis triggered by GitHub push events.

## Architecture

```
GitHub Repository
    ↓ (push event)
GitHub Webhook
    ↓ (HTTP POST)
Webhook Server (FastAPI)
    ↓ (background task)
Autonomous Agent
    ↓ (analysis complete)
GitHub Comment + Results
```

## Prerequisites

1. **GitHub Repository** - The repo you want to monitor
2. **GitHub Personal Access Token** - For API access
3. **Groq API Key** - For LLM analysis
4. **Public URL** - For webhook (use ngrok for local testing)

---

## Step 1: Get GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Code Quality Monitor"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `write:discussion` (Write access to discussions)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

---

## Step 2: Configure Environment Variables

Update your `.env` file:

```bash
# Groq API (for LLM)
GROQ_API_KEY=gsk_your_groq_key_here

# GitHub API (for repository access)
GITHUB_TOKEN=ghp_your_github_token_here

# Webhook Secret (optional, for security)
WEBHOOK_SECRET=your_random_secret_here
```

---

## Step 3: Start the Webhook Server

### Option A: Local Testing with ngrok

1. **Install ngrok** (if not installed):
   ```bash
   # Download from https://ngrok.com/download
   # Or use chocolatey on Windows:
   choco install ngrok
   ```

2. **Start the webhook server**:
   ```bash
   python webhook_server.py
   ```
   
   You should see:
   ```
   🚀 Starting Code Quality Monitor Webhook Server
   📍 Webhook URL: http://localhost:8000/webhook/github
   ```

3. **In a new terminal, start ngrok**:
   ```bash
   ngrok http 8000
   ```
   
   You'll get a public URL like:
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:8000
   ```

4. **Your webhook URL is**: `https://abc123.ngrok.io/webhook/github`

### Option B: Deploy to Cloud

Deploy to Render, Railway, or Heroku:

**Render.com (Free tier):**
1. Push code to GitHub
2. Go to render.com → New → Web Service
3. Connect your repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `python webhook_server.py`
6. Add environment variables (GROQ_API_KEY, GITHUB_TOKEN)
7. Deploy!

Your webhook URL: `https://your-app.onrender.com/webhook/github`

---

## Step 4: Configure GitHub Webhook

1. Go to your GitHub repository
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-url/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: (optional) same as WEBHOOK_SECRET in .env
   - **Which events**: Select "Just the push event"
   - **Active**: ✅ Checked
4. Click **Add webhook**

GitHub will send a ping event to test the connection.

---

## Step 5: Test the Integration

### Test 1: Manual API Call

```bash
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/owner/repo"
```

### Test 2: Push to Repository

1. Make a change to your repository
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test webhook trigger"
   git push
   ```

3. Check the webhook server logs:
   ```
   📨 Received push event:
      Repository: https://github.com/owner/repo
      Commit: abc12345
      Message: Test webhook trigger
   
   🔍 Starting analysis...
   🤖 Running autonomous agent...
   ✅ Analysis complete!
   ```

4. Check GitHub - you should see a comment on the commit with the analysis results!

---

## How It Works

### 1. Push Event Triggered
```
Developer pushes code → GitHub sends webhook → Server receives event
```

### 2. Analysis Queued
```
Server extracts:
- Repository URL
- Commit SHA
- Changed files

Queues background task
```

### 3. Autonomous Agent Runs
```
THINK  → Parse changed files
PLAN   → Create analysis plan
EXECUTE → Run 4 tools:
           • code_scanner
           • test_case_generator
           • issue_prioritizer
           • report_writer
REVIEW → Score quality (1-10)
UPDATE → Retry if score < 7
```

### 4. Results Posted
```
Agent posts comment to GitHub commit with:
- Issues found
- Test cases generated
- Recommendations
```

---

## API Endpoints

### GET /
Health check
```bash
curl http://localhost:8000/
```

### GET /history
View last 10 analyses
```bash
curl http://localhost:8000/history
```

### POST /webhook/github
GitHub webhook endpoint (called automatically)

### POST /analyze
Manual analysis trigger
```bash
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/owner/repo&commit_sha=abc123"
```

---

## Troubleshooting

### Webhook not triggering

1. **Check webhook deliveries** in GitHub:
   - Settings → Webhooks → Recent Deliveries
   - Look for errors (401, 404, 500)

2. **Check server logs**:
   - Should see "📨 Received push event"
   - If not, webhook isn't reaching server

3. **Verify ngrok is running**:
   - ngrok must be active for local testing
   - Check ngrok dashboard: http://localhost:4040

### Analysis failing

1. **Check API keys**:
   ```bash
   # Test Groq API
   python test_all_groq_models.py
   
   # Test GitHub API
   python -c "from github import Github; g = Github('your_token'); print(g.get_user().login)"
   ```

2. **Check repository access**:
   - Token must have `repo` scope
   - Repository must be accessible

3. **Check logs**:
   - Server prints detailed error messages
   - Look for "❌ Error during analysis"

### Comments not posting

1. **Verify GITHUB_TOKEN** has write permissions
2. **Check token scopes** include `repo`
3. **Verify repository ownership** - token must have access

---

## Security Best Practices

### 1. Use Webhook Secret
```bash
# In .env
WEBHOOK_SECRET=your_random_secret_here
```

Server will verify GitHub signature before processing.

### 2. Restrict Token Permissions
Only grant necessary scopes:
- ✅ `repo` (if analyzing private repos)
- ✅ `public_repo` (if only public repos)
- ❌ Don't grant admin or delete permissions

### 3. Use Environment Variables
Never commit API keys to git!

### 4. Deploy with HTTPS
Always use HTTPS in production (Render/Railway provide this automatically)

---

## Advanced Usage

### Analyze Specific Commit
```bash
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/owner/repo&commit_sha=abc123def456"
```

### Analyze Full Repository
```bash
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/owner/repo"
```

### View Analysis History
```bash
curl http://localhost:8000/history | python -m json.tool
```

---

## Next Steps

1. ✅ Set up webhook for your repository
2. ✅ Test with a push event
3. ✅ Verify comments appear on commits
4. 🔄 Deploy to production (Render/Railway)
5. 🔄 Add to multiple repositories
6. 🔄 Customize analysis criteria in `agent/reviewer.py`

---

## Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: See PROJECT_PLAN.md for architecture details
- **Webhook Logs**: Check server output for debugging

---

**You now have automatic code quality monitoring! 🎉**

Every push triggers analysis, and results appear as GitHub comments automatically.