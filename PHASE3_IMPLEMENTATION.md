# Phase 3: GitHub API Integration - Implementation Guide

## Goal
Automatically trigger code quality analysis when code is pushed to a GitHub repository.

## Architecture

```
GitHub Push Event
    ↓
GitHub Webhook
    ↓
FastAPI Webhook Endpoint
    ↓
Background Task Queue
    ↓
Autonomous Agent (5-step loop)
    ↓
Results stored + displayed
```

## Implementation Steps

### Step 1: Install Dependencies

```bash
pip install PyGithub fastapi uvicorn python-multipart aiofiles
```

### Step 2: Create GitHub Integration Module

**File: `agent/tools/github_integration.py`**
- Fetch repository files
- Get commit changes
- Clone repository temporarily
- Post review comments

### Step 3: Create Webhook Server

**File: `webhook_server.py`**
- FastAPI server to receive GitHub webhooks
- Background task processing
- Queue management

### Step 4: Update Main Application

**File: `main.py`**
- Add GitHub repository URL input
- Add webhook setup instructions
- Show recent analysis history

### Step 5: Configure GitHub Webhook

1. Go to GitHub repo → Settings → Webhooks
2. Add webhook URL: `http://your-server:8000/webhook/github`
3. Select "Push events"
4. Save

## Features

### Automatic Triggers
- ✅ Triggered on every push
- ✅ Analyzes changed files
- ✅ Posts results as GitHub comments
- ✅ Creates issues for critical bugs

### Manual Triggers
- ✅ Analyze any GitHub repository
- ✅ Analyze specific commits
- ✅ Analyze pull requests

## Testing

### Local Testing
1. Use ngrok to expose local server
2. Configure GitHub webhook to ngrok URL
3. Push code and verify trigger

### Production
1. Deploy to cloud (Render, Railway, etc.)
2. Configure webhook to production URL
3. Monitor logs

## Timeline

- Step 1: Install dependencies (5 min)
- Step 2: GitHub integration (1 hour)
- Step 3: Webhook server (1.5 hours)
- Step 4: Update UI (1 hour)
- Step 5: Testing (30 min)

**Total: ~4 hours**