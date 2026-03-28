"""
GitHub Webhook Server
Receives push events from GitHub and triggers code quality analysis
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Import agent components
from agent import loop
from agent.tools import github_integration

load_dotenv()

app = FastAPI(title="Code Quality Monitor Webhook Server")

# Store analysis results
analysis_history = []

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


def verify_signature(request: Request, payload: bytes) -> bool:
    """Verify GitHub webhook signature"""
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
        
    import hmac
    import hashlib
    
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature:
        return False
        
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


async def analyze_repository(repo_url: str, commit_sha: Optional[str] = None):
    """
    Run code quality analysis on repository
    
    Args:
        repo_url: GitHub repository URL
        commit_sha: Optional commit SHA to analyze specific commit
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Starting analysis for {repo_url}")
        if commit_sha:
            print(f"📝 Commit: {commit_sha[:8]}")
        print(f"{'='*60}\n")
        
        # Fetch repository or commit changes
        if commit_sha:
            repo_data = github_integration.fetch_commit_changes(
                repo_url, commit_sha, GITHUB_TOKEN
            )
            if not repo_data['success']:
                print(f"❌ Error: {repo_data['error']}")
                return
            
            # Create temporary directory with changed files
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix='webhook_analysis_')
            
            for filename, file_data in repo_data['changed_files'].items():
                filepath = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_data['content'])
            
            repo_path = temp_dir
            analysis_type = f"Commit {commit_sha[:8]}"
            
        else:
            repo_data = github_integration.fetch_repository(repo_url, GITHUB_TOKEN)
            if not repo_data['success']:
                print(f"❌ Error: {repo_data['error']}")
                return
            
            # Create temporary directory with all files
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix='webhook_analysis_')
            
            for filename, content in repo_data['files'].items():
                filepath = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            repo_path = temp_dir
            analysis_type = "Full Repository"
        
        # Run autonomous agent
        print(f"🤖 Running autonomous agent on {analysis_type}...")
        
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        result = loop.run(
            client=client,
            model="llama-3.1-8b-instant",
            repo_path=repo_path,
            max_loops=3
        )
        
        # Store result
        analysis_record = {
            'timestamp': datetime.now().isoformat(),
            'repo_url': repo_url,
            'commit_sha': commit_sha,
            'analysis_type': analysis_type,
            'result': result,
            'success': result.get('success', False)
        }
        analysis_history.append(analysis_record)
        
        # Keep only last 50 analyses
        if len(analysis_history) > 50:
            analysis_history.pop(0)
        
        # Post comment to GitHub if commit analysis
        if commit_sha and GITHUB_TOKEN:
            comment = f"""## 🤖 Automated Code Quality Analysis

**Analysis Type:** {analysis_type}
**Status:** {'✅ Passed' if result.get('success') else '❌ Failed'}

### Summary
{result.get('summary', 'Analysis completed')}

---
*Powered by AI Code Quality Monitor*
"""
            github_integration.post_review_comment(
                repo_url, commit_sha, comment, GITHUB_TOKEN
            )
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print(f"\n✅ Analysis complete!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}\n")
        import traceback
        traceback.print_exc()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Code Quality Monitor Webhook Server",
        "analyses_completed": len(analysis_history)
    }


@app.get("/history")
async def get_history():
    """Get analysis history"""
    return {
        "total": len(analysis_history),
        "analyses": analysis_history[-10:]  # Last 10
    }


@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    GitHub webhook endpoint
    Receives push events and triggers analysis
    """
    try:
        # Get payload
        payload = await request.body()
        
        # Verify signature
        if not verify_signature(request, payload):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        data = json.loads(payload)
        
        # Get event type
        event_type = request.headers.get("X-GitHub-Event", "")
        
        if event_type == "ping":
            return {"message": "Webhook configured successfully!"}
        
        if event_type == "push":
            # Extract repository and commit info
            repo_url = data['repository']['html_url']
            commits = data.get('commits', [])
            
            if commits:
                # Analyze the latest commit
                latest_commit = commits[-1]
                commit_sha = latest_commit['id']
                
                print(f"\n📨 Received push event:")
                print(f"   Repository: {repo_url}")
                print(f"   Commit: {commit_sha[:8]}")
                print(f"   Message: {latest_commit['message']}")
                
                # Trigger analysis in background
                background_tasks.add_task(
                    analyze_repository,
                    repo_url,
                    commit_sha
                )
                
                return {
                    "status": "accepted",
                    "message": "Analysis queued",
                    "commit": commit_sha[:8]
                }
            else:
                return {"status": "ignored", "message": "No commits in push"}
        
        return {"status": "ignored", "message": f"Event type '{event_type}' not handled"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def manual_analysis(
    repo_url: str,
    commit_sha: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Manual analysis endpoint
    Trigger analysis via API call
    """
    if background_tasks:
        background_tasks.add_task(analyze_repository, repo_url, commit_sha)
        return {
            "status": "accepted",
            "message": "Analysis queued",
            "repo": repo_url
        }
    else:
        await analyze_repository(repo_url, commit_sha)
        return {
            "status": "completed",
            "message": "Analysis finished",
            "repo": repo_url
        }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Code Quality Monitor Webhook Server")
    print("="*60)
    print(f"\n📍 Webhook URL: http://localhost:8000/webhook/github")
    print(f"📊 History URL: http://localhost:8000/history")
    print(f"🔧 Manual trigger: POST http://localhost:8000/analyze")
    print(f"\n{'='*60}\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)