"""
GitHub Integration Tool
Fetches code from GitHub repositories and analyzes commits
"""
import os
import tempfile
import shutil
from github import Github, GithubException
from typing import Dict, List, Optional


def fetch_repository(repo_url: str, github_token: Optional[str] = None) -> Dict:
    """
    Fetch repository files from GitHub
    
    Args:
        repo_url: GitHub repository URL (e.g., 'owner/repo' or full URL)
        github_token: Optional GitHub personal access token for private repos
        
    Returns:
        Dictionary with repository info and file contents
    """
    try:
        # Extract owner/repo from URL
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        # Initialize GitHub client
        g = Github(github_token) if github_token else Github()
        
        # Get repository
        repo = g.get_repo(owner_repo)
        
        # Get default branch
        default_branch = repo.default_branch
        
        # Get all files from repository
        contents_list = repo.get_contents("", ref=default_branch)
        if not isinstance(contents_list, list):
            contents_list = [contents_list]
        
        files = {}
        
        while contents_list:
            file_content = contents_list.pop(0)
            if file_content.type == "dir":
                dir_contents = repo.get_contents(file_content.path, ref=default_branch)
                if isinstance(dir_contents, list):
                    contents_list.extend(dir_contents)
                else:
                    contents_list.append(dir_contents)
            else:
                # Only process code files
                if file_content.path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rb')):
                    try:
                        files[file_content.path] = file_content.decoded_content.decode('utf-8')
                    except:
                        pass  # Skip binary or unreadable files
        
        return {
            'success': True,
            'repo_name': repo.full_name,
            'description': repo.description or 'No description',
            'language': repo.language or 'Unknown',
            'stars': repo.stargazers_count,
            'default_branch': default_branch,
            'files': files,
            'file_count': len(files)
        }
        
    except GithubException as e:
        return {
            'success': False,
            'error': f'GitHub API error: {str(e)}',
            'files': {}
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching repository: {str(e)}',
            'files': {}
        }


def fetch_commit_changes(repo_url: str, commit_sha: str, github_token: Optional[str] = None) -> Dict:
    """
    Fetch files changed in a specific commit
    
    Args:
        repo_url: GitHub repository URL
        commit_sha: Commit SHA to analyze
        github_token: Optional GitHub token
        
    Returns:
        Dictionary with changed files and their contents
    """
    try:
        # Extract owner/repo
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        # Initialize GitHub client
        g = Github(github_token) if github_token else Github()
        repo = g.get_repo(owner_repo)
        
        # Get commit
        commit = repo.get_commit(commit_sha)
        
        # Get changed files
        changed_files = {}
        for file in commit.files:
            if file.filename.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rb')):
                try:
                    # Get file content at this commit
                    content_file = repo.get_contents(file.filename, ref=commit_sha)
                    if not isinstance(content_file, list):
                        changed_files[file.filename] = {
                            'content': content_file.decoded_content.decode('utf-8'),
                            'status': file.status,  # added, modified, removed
                            'additions': file.additions,
                            'deletions': file.deletions,
                            'changes': file.changes
                        }
                except:
                    pass
        
        return {
            'success': True,
            'commit_sha': commit_sha,
            'commit_message': commit.commit.message,
            'author': commit.commit.author.name,
            'date': commit.commit.author.date.isoformat(),
            'changed_files': changed_files,
            'file_count': len(changed_files)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching commit: {str(e)}',
            'changed_files': {}
        }


def clone_to_temp(repo_url: str, github_token: Optional[str] = None) -> str:
    """
    Clone repository to temporary directory
    
    Args:
        repo_url: GitHub repository URL
        github_token: Optional GitHub token
        
    Returns:
        Path to temporary directory with cloned repo
    """
    import subprocess
    
    temp_dir = tempfile.mkdtemp(prefix='github_agent_')
    
    try:
        # Build clone URL with token if provided
        if github_token and 'github.com' in repo_url:
            clone_url = repo_url.replace('https://', f'https://{github_token}@')
        else:
            clone_url = repo_url
            
        # Clone repository
        subprocess.run(
            ['git', 'clone', '--depth', '1', clone_url, temp_dir],
            check=True,
            capture_output=True
        )
        
        return temp_dir
        
    except subprocess.CalledProcessError as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f'Failed to clone repository: {e.stderr.decode()}')


def cleanup_temp(temp_dir: str):
    """Remove temporary directory"""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def post_review_comment(repo_url: str, commit_sha: str, comment: str, github_token: str) -> bool:
    """
    Post a review comment on a commit
    
    Args:
        repo_url: GitHub repository URL
        commit_sha: Commit SHA to comment on
        comment: Comment text
        github_token: GitHub token (required for posting)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        g = Github(github_token)
        repo = g.get_repo(owner_repo)
        commit = repo.get_commit(commit_sha)
        
        # Create commit comment
        commit.create_comment(comment)
        
        return True
        
    except Exception as e:
        print(f"Error posting comment: {e}")
        return False


def list_all_code_files(repo_url: str, github_token: str, file_extensions: Optional[List[str]] = None) -> Dict:
    """
    List ALL code files in repository with metadata
    
    Args:
        repo_url: GitHub repository URL
        github_token: GitHub token (required)
        file_extensions: List of extensions to include (default: common code files)
        
    Returns:
        Dictionary with file list and metadata
    """
    if file_extensions is None:
        file_extensions = ['.py', '.js', '.ts', '.java', '.md', '.cpp', '.c', '.go', '.rb', '.php', '.swift', '.kt']
    
    try:
        # Extract owner/repo
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(owner_repo)
        
        # Get default branch
        default_branch = repo.default_branch
        
        # Get all files
        contents_list = repo.get_contents("", ref=default_branch)
        if not isinstance(contents_list, list):
            contents_list = [contents_list]
        
        files = []
        
        while contents_list:
            file_content = contents_list.pop(0)
            if file_content.type == "dir":
                dir_contents = repo.get_contents(file_content.path, ref=default_branch)
                if isinstance(dir_contents, list):
                    contents_list.extend(dir_contents)
                else:
                    contents_list.append(dir_contents)
            else:
                # Check if file extension matches
                ext = os.path.splitext(file_content.path)[1]
                if ext in file_extensions:
                    files.append({
                        'path': file_content.path,
                        'size': file_content.size,
                        'type': 'file',
                        'extension': ext,
                        'sha': file_content.sha
                    })
        
        return {
            'success': True,
            'repo_name': repo.full_name,
            'default_branch': default_branch,
            'files': files,
            'file_count': len(files)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error listing files: {str(e)}',
            'files': []
        }


def get_changed_files_between_commits(repo_url: str, base_sha: str, head_sha: str, github_token: str) -> Dict:
    """
    Get files changed between two commits
    
    Args:
        repo_url: GitHub repository URL
        base_sha: Base commit SHA (older)
        head_sha: Head commit SHA (newer)
        github_token: GitHub token (required)
        
    Returns:
        Dictionary with changed files categorized by status
    """
    try:
        # Extract owner/repo
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(owner_repo)
        
        # Compare commits
        comparison = repo.compare(base_sha, head_sha)
        
        # Categorize files by status
        modified = []
        added = []
        deleted = []
        
        for file in comparison.files:
            file_info = {
                'path': file.filename,
                'additions': file.additions,
                'deletions': file.deletions,
                'changes': file.changes,
                'status': file.status
            }
            
            if file.status == 'modified':
                modified.append(file_info)
            elif file.status == 'added':
                added.append(file_info)
            elif file.status in ['removed', 'deleted']:
                deleted.append(file_info)
        
        return {
            'success': True,
            'base_sha': base_sha,
            'head_sha': head_sha,
            'modified': modified,
            'added': added,
            'deleted': deleted,
            'total_changes': len(modified) + len(added) + len(deleted)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error comparing commits: {str(e)}',
            'modified': [],
            'added': [],
            'deleted': []
        }


def get_latest_commit_sha(repo_url: str, github_token: str) -> Dict:
    """
    Get latest commit SHA from default branch
    
    Args:
        repo_url: GitHub repository URL
        github_token: GitHub token (required)
        
    Returns:
        Dictionary with commit information
    """
    try:
        # Extract owner/repo
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(owner_repo)
        
        # Get latest commit from default branch
        branch = repo.get_branch(repo.default_branch)
        commit = branch.commit
        
        return {
            'success': True,
            'sha': commit.sha,
            'message': commit.commit.message,
            'author': commit.commit.author.name,
            'date': commit.commit.author.date.isoformat(),
            'url': commit.html_url
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error getting latest commit: {str(e)}'
        }


def fetch_file_content(repo_url: str, file_path: str, commit_sha: str, github_token: str) -> Dict:
    """
    Fetch specific file content at specific commit
    
    Args:
        repo_url: GitHub repository URL
        file_path: Path to file in repository
        commit_sha: Commit SHA to fetch from
        github_token: GitHub token (required)
        
    Returns:
        Dictionary with file content
    """
    try:
        # Extract owner/repo
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            owner_repo = f"{parts[-2]}/{parts[-1]}"
        else:
            owner_repo = repo_url
            
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(owner_repo)
        
        # Get file content at specific commit
        content_file = repo.get_contents(file_path, ref=commit_sha)
        
        if isinstance(content_file, list):
            return {
                'success': False,
                'error': 'Path is a directory, not a file'
            }
        
        return {
            'success': True,
            'path': file_path,
            'content': content_file.decoded_content.decode('utf-8'),
            'size': content_file.size,
            'sha': content_file.sha
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching file: {str(e)}'
        }


# Tool metadata for the agent
TOOL_METADATA = {
    "name": "github_integration",
    "description": "Fetches code from GitHub repositories for analysis",
    "functions": {
        "fetch_repository": "Fetch all code files from a GitHub repository",
        "fetch_commit_changes": "Fetch files changed in a specific commit",
        "list_all_code_files": "List all code files with metadata",
        "get_changed_files_between_commits": "Get files changed between two commits",
        "get_latest_commit_sha": "Get latest commit SHA and info",
        "fetch_file_content": "Fetch specific file content at commit",
        "clone_to_temp": "Clone repository to temporary directory for analysis",
        "post_review_comment": "Post analysis results as a commit comment"
    }
}
