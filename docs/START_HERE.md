# 🚀 Quick Start Guide - Test Your Webhook

## What You'll Do
Test that pushing code to GitHub automatically triggers code quality analysis.

---

## ⚡ Super Quick Test (2 minutes)

### Step 1: Start the Server
```bash
python webhook_server.py
```

### Step 2: Open Dashboard
Open in browser: **`dashboard.html`** (double-click the file)

You'll see:
- ✅ Server status (should show "Online")
- 📊 Statistics (analyses count, success rate)
- 📝 Recent analyses history

### Step 3: Test Manually
In another terminal:
```bash
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/Kaushik-SPACEZ/github-agent"
```

### Step 4: Watch the Dashboard
- Refresh the dashboard (or wait 5 seconds for auto-refresh)
- You should see your analysis appear!

---

## 🌐 Full Test with Git Push (10 minutes)

### Prerequisites
- Install ngrok: https://ngrok.com/download

### Step 1: Start Server
**Terminal 1:**
```bash
python webhook_server.py
```

### Step 2: Start ngrok
**Terminal 2:**
```bash
ngrok http 8000
```

Copy the https URL (e.g., `https://abc123.ngrok.io`)

### Step 3: Configure GitHub Webhook

1. Go to: https://github.com/Kaushik-SPACEZ/github-agent/settings/hooks
2. Click "Add webhook"
3. Paste your ngrok URL + `/webhook/github`
   - Example: `https://abc123.ngrok.io/webhook/github`
4. Content type: `application/json`
5. Events: "Just the push event"
6. Click "Add webhook"

### Step 4: Test with Git Push

```bash
# Make a small change
echo "# Test" > test.txt

# Commit and push
git add test.txt
git commit -m "Test webhook"
git push
```

### Step 5: Watch the Magic! ✨

**In Terminal 1, you'll see:**
```
📨 Received push event:
   Repository: https://github.com/Kaushik-SPACEZ/github-agent
   Commit: abc12345
   Message: Test webhook

🔍 Starting analysis...
🤖 Running autonomous agent...
✅ Analysis complete!
```

**In the Dashboard:**
- New analysis appears automatically
- Shows commit SHA, timestamp, status

**On GitHub:**
- Go to your commit
- You'll see a comment with analysis results!

---

## 📊 Dashboard Features

Open `dashboard.html` in your browser to see:

### Real-time Monitoring
- 🟢 Server status (online/offline)
- 📈 Total analyses count
- ✅ Success rate percentage
- ⏰ Last analysis time

### Analysis History
- All recent analyses
- Commit SHAs
- Timestamps
- Success/failure status
- Auto-refreshes every 5 seconds

---

## 🔍 Troubleshooting

### Dashboard shows "Offline"
**Solution:** Start the webhook server
```bash
python webhook_server.py
```

### No analyses appearing
**Solution:** Trigger one manually
```bash
curl -X POST "http://localhost:8000/analyze?repo_url=https://github.com/Kaushik-SPACEZ/github-agent"
```

### Webhook not triggering on push
**Check:**
1. ngrok is running
2. GitHub webhook URL is correct
3. GitHub webhook shows green checkmark
4. Check "Recent Deliveries" in GitHub webhook settings

---

## 📝 What Happens During Analysis

```
1. GitHub Push Event
   ↓
2. Webhook Server Receives Event
   ↓
3. Fetch Changed Files from GitHub
   ↓
4. Autonomous Agent Runs (5 steps):
   • THINK → Parse files
   • PLAN → Create analysis plan
   • EXECUTE → Run 4 tools
   • REVIEW → Score quality
   • UPDATE → Retry if needed
   ↓
5. Results Posted to GitHub
   ↓
6. Dashboard Updates
```

---

## 🎯 Expected Results

After pushing code, you should see:

**✅ In Terminal:**
- "📨 Received push event"
- "🤖 Running autonomous agent"
- "✅ Analysis complete"

**✅ In Dashboard:**
- New entry in history
- Updated statistics
- Green success indicator

**✅ On GitHub:**
- Comment on your commit
- Analysis results with:
  - Issues found
  - Test cases generated
  - Recommendations

---

## 🚀 Next Steps

1. ✅ Test locally with dashboard
2. ✅ Test with git push (using ngrok)
3. 🔄 Deploy to production (Render/Railway)
4. 🔄 Add to multiple repositories

---

## 📚 More Information

- **Full Setup Guide:** `GITHUB_SETUP_GUIDE.md`
- **Testing Guide:** `TEST_WEBHOOK_GUIDE.md`
- **Project Plan:** `PROJECT_PLAN.md`

---

**Ready to test? Start with the Super Quick Test above!** 🎉