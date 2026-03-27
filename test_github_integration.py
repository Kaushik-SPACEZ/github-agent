"""
Test GitHub Integration
Verifies that GitHub API access works correctly
"""
import os
from dotenv import load_dotenv
from agent.tools import github_integration

load_dotenv()

print("=" * 70)
print("TESTING GITHUB INTEGRATION")
print("=" * 70)

# Get GitHub token
github_token = os.getenv("GITHUB_TOKEN", "")

if not github_token:
    print("\n⚠️  No GITHUB_TOKEN found in .env")
    print("   You can still test with public repositories (rate limited)")
    print("   Get a token at: https://github.com/settings/tokens\n")
else:
    print(f"\n✅ GitHub token found: {github_token[:10]}...{github_token[-5:]}\n")

# Test 1: Fetch a public repository
print("\n" + "="*70)
print("TEST 1: Fetch Public Repository")
print("="*70)

test_repo = "Kaushik-SPACEZ/github-agent"  # Your repo!
print(f"\nFetching: {test_repo}")

result = github_integration.fetch_repository(test_repo, github_token)

if result['success']:
    print(f"\n✅ SUCCESS!")
    print(f"   Repository: {result['repo_name']}")
    print(f"   Description: {result['description']}")
    print(f"   Language: {result['language']}")
    print(f"   Stars: {result['stars']}")
    print(f"   Files found: {result['file_count']}")
    print(f"\n   Sample files:")
    for i, filepath in enumerate(list(result['files'].keys())[:5]):
        print(f"      {i+1}. {filepath}")
    if result['file_count'] > 5:
        print(f"      ... and {result['file_count'] - 5} more")
else:
    print(f"\n❌ FAILED: {result['error']}")

# Test 2: Fetch commit changes (if we have a commit SHA)
print("\n" + "="*70)
print("TEST 2: Fetch Commit Changes")
print("="*70)

print(f"\nTo test commit fetching, you need a commit SHA.")
print(f"Get one from: https://github.com/{test_repo}/commits")
print(f"\nExample usage:")
print(f"  result = github_integration.fetch_commit_changes(")
print(f"      '{test_repo}',")
print(f"      'abc123def456...',  # commit SHA")
print(f"      github_token")
print(f"  )")

# Test 3: Verify we can analyze the fetched code
print("\n" + "="*70)
print("TEST 3: Verify Code Analysis Ready")
print("="*70)

if result['success'] and result['file_count'] > 0:
    print(f"\n✅ Ready for analysis!")
    print(f"   {result['file_count']} code files can be analyzed")
    print(f"   These files will be passed to the autonomous agent")
    print(f"\n   To analyze this repository:")
    print(f"   1. Start webhook server: python webhook_server.py")
    print(f"   2. Call API: curl -X POST 'http://localhost:8000/analyze?repo_url=https://github.com/{test_repo}'")
else:
    print(f"\n❌ Not ready - no files found or fetch failed")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if result['success']:
    print("\n✅ GitHub integration is working!")
    print("\nNext steps:")
    print("  1. Start webhook server: python webhook_server.py")
    print("  2. Set up GitHub webhook (see GITHUB_SETUP_GUIDE.md)")
    print("  3. Push code to trigger automatic analysis")
else:
    print("\n❌ GitHub integration needs attention")
    print("\nTroubleshooting:")
    print("  1. Check internet connection")
    print("  2. Verify repository URL is correct")
    print("  3. If private repo, add GITHUB_TOKEN to .env")
    print("  4. Check GitHub API rate limits")

print("\n" + "="*70 + "\n")