# Testing Webhook with Git Push - Step by Step

## Goal
Test that pushing code to GitHub automatically triggers the code quality analysis.

## Prerequisites
- ✅ Groq API key in .env
- ✅ GitHub token in .env
- ✅ Repository: Kaushik-SPACEZ/github-agent

---

## Option 1: Test Locally with ngrok (Recommended for Testing)

### Step 1: Install ngrok

**Windows (using Chocolatey):**
```bash
choco install ngrok
```

**Or download from:** https://ngrok.com/download

### Step 2: Start the Webhook Server

Open **Terminal 1**:
```bash
cd c:\Users\I768970\github-agent
python webhook_server.py
```

You should see:
```
🚀 Starting Code Quality Monitor Webhook Server
📍 Webhook URL: http://localhost:8000/webhook/github
```

### Step 3: Start ngrok

Open **Terminal 2**:
```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the https URL** (e.g., `https://abc123.ngrok.io`)

### Step 4: Configure GitHub Webhook

1. Go to: https://github.com/Kaushik-SPACEZ/github-agent/settings/hooks
2. Click **"Add webhook"**
3. Fill in:
   - **Payload URL**: `https://abc123.ngrok.io/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: (leave empty for now)
   - **Which events**: Select "Just the push event"
   - **Active**: ✅ Checked
4. Click **"Add webhook"**

GitHub will send a test "ping" event. You should see in Terminal 1:
```
Webhook configured successfully!
```

### Step 5: Test with Git Push

Make a small change to test:

```bash
# Create a test file
echo "# Test webhook" > test_webhook.txt

# Commit and push
git add test_webhook.txt
git commit -m "Test webhook trigger"
git push
```

### Step 6: Watch the Magic! ✨

**In Terminal 1 (webhook server), you'll see:**
```
📨 Received push event:
   Repository: https://github.com/Kaushik-SPACEZ/github-agent
   Commit: abc12345
   Message: Test webhook trigger

🔍 Starting analysis...
🤖 Running autonomous agent...

THINK → Parsing repository...
PLAN → Creating analysis plan...
EXECUTE → Running tools...
REVIEW → Scoring quality...

✅ Analysis complete!
```

**On GitHub:**
- Go to your commit: https://github.com/Kaushik-SPACEZ/github-agent/commits
- You should see a **comment** on your commit with the analysis results!

---

## Option 2: Test with Streamlit UI (Visual Testing)

### Step 1: Update main.py to Support GitHub URLs

The current Streamlit app analyzes local directories. Let's add GitHub support:

```bash
# Run the Streamlit app
streamlit run main.py
```

### Step 2: Use the UI

1. Open browser: http://localhost:8501
2. Enter repository path: `./mock_repo` (or any local path)
3. Click "Analyze Code Quality"
4. Watch the 5 steps light up!

**Note:** To analyze GitHub repos directly in the UI, we'd need to modify main.py to accept GitHub URLs.

---

## Option 3: Test via API (No Webhook Setup Needed)

### Step 1: Start Webhook Server

```bash
python webhook_server.py
```

### Step 2: Trigger Analysis via API

**In another terminal or browser:**

```bash
# Analyze your entire repository
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/Kaushik-SPACEZ/github-agent"
```

**Or open in browser:**
```
http://localhost:8000/analyze?repo_url=https://github.com/Kaushik-SPACEZ/github-agent
```

### Step 3: View Results

**Check analysis history:**
```bash
curl http://localhost:8000/history
```

**Or in browser:**
```
http://localhost:8000/history
```

---

## Troubleshooting

### Webhook not triggering

**Check 1: Webhook deliveries on GitHub**
1. Go to: https://github.com/Kaushik-SPACEZ/github-agent/settings/hooks
2. Click on your webhook
3. Click "Recent Deliveries"
4. Look for errors (401, 404, 500)

**Check 2: ngrok is running**
- ngrok must be active
- Check dashboard: http://localhost:4040

**Check 3: Server logs**
- Look for "📨 Received push event" in Terminal 1
- If not appearing, webhook isn't reaching server

### Analysis failing

**Check API keys:**
```bash
python test_all_groq_models.py
python test_github_integration.py
```

**Check server logs:**
- Look for error messages in Terminal 1
- Common issues:
  - API rate limits
  - Invalid tokens
  - Network issues

### ngrok URL expired

ngrok free tier URLs expire after 2 hours. If expired:
1. Restart ngrok
2. Get new URL
3. Update GitHub webhook with new URL

---

## Visual Confirmation Checklist

### ✅ Webhook Working When You See:

**In Terminal 1 (webhook server):**
- [ ] "📨 Received push event"
- [ ] "🔍 Starting analysis"
- [ ] "🤖 Running autonomous agent"
- [ ] "✅ Analysis complete"

**On GitHub:**
- [ ] Webhook shows green checkmark in settings
- [ ] Recent deliveries show 200 OK
- [ ] Comment appears on commit

**In Browser (http://localhost:4040):**
- [ ] ngrok shows POST request to /webhook/github
- [ ] Status: 200 OK

---

## Quick Test Commands

```bash
# 1. Start webhook server
python webhook_server.py

# 2. In another terminal, test manually
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/Kaushik-SPACEZ/github-agent"

# 3. Check if server is running
curl http://localhost:8000/

# 4. View analysis history
curl http://localhost:8000/history
```

---

## Expected Output

### Successful Analysis Output:

```
======================================================================
🔍 Starting analysis for https://github.com/Kaushik-SPACEZ/github-agent
======================================================================

🤖 Running autonomous agent on Full Repository...

AUTONOMOUS LOOP: 1 of 3

THINK → Parsing repository structure...
✓ Found 25 Python files

PLAN → Creating analysis plan...
✓ Plan: code_scanner → test_case_generator → issue_prioritizer → report_writer

EXECUTE → Running tools...
✓ code_scanner: Found 19 issues
✓ test_case_generator: Generated 5 test cases
✓ issue_prioritizer: Ranked by severity
✓ report_writer: Compiled report

REVIEW → Scoring quality...
✓ Score: 8.2/10 - PASSED

✅ Analysis complete!
======================================================================
```

---

## Next Steps After Testing

1. ✅ Verify webhook works with git push
2. ✅ Check GitHub comments appear
3. 🔄 Deploy to production (Render/Railway)
4. 🔄 Add webhook to multiple repositories
5. 🔄 Customize analysis criteria

---

## Production Deployment (Optional)

### Deploy to Render.com (Free)

1. Push code to GitHub
2. Go to https://render.com
3. New → Web Service
4. Connect repository
5. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python webhook_server.py`
   - Add environment variables (GROQ_API_KEY, GITHUB_TOKEN)
6. Deploy!

Your webhook URL: `https://your-app.onrender.com/webhook/github`

Update GitHub webhook with this production URL.

---

**You're ready to test! Start with Option 1 (ngrok) for the full experience.** 🚀