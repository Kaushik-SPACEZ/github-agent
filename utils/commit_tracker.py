"""
Commit Tracker
Stores and retrieves last analyzed commit SHA for repositories
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, List


class CommitTracker:
    """Track analyzed commits for repositories"""
    
    def __init__(self, storage_file: str = 'commit_tracker.json'):
        self.storage_file = storage_file
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load data from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'repositories': {}}
        return {'repositories': {}}
    
    def _save(self):
        """Save data to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _normalize_repo_url(self, repo_url: str) -> str:
        """Normalize repo URL to owner/repo format"""
        # Remove https://github.com/ prefix if present
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            return f"{parts[-2]}/{parts[-1]}"
        return repo_url
    
    def get_last_commit(self, repo_url: str) -> Optional[str]:
        """
        Get last analyzed commit SHA for repository
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Commit SHA or None if never analyzed
        """
        repo_key = self._normalize_repo_url(repo_url)
        repo_data = self.data['repositories'].get(repo_key)
        
        if repo_data:
            return repo_data.get('last_analyzed_commit')
        return None
    
    def save_commit(self, repo_url: str, commit_sha: str, analyzed_files: List[str]):
        """
        Save analyzed commit SHA and files
        
        Args:
            repo_url: GitHub repository URL
            commit_sha: Commit SHA that was analyzed
            analyzed_files: List of file paths that were analyzed
        """
        repo_key = self._normalize_repo_url(repo_url)
        
        self.data['repositories'][repo_key] = {
            'last_analyzed_commit': commit_sha,
            'last_analyzed_date': datetime.now().isoformat(),
            'analyzed_files': analyzed_files,
            'analysis_count': self.data['repositories'].get(repo_key, {}).get('analysis_count', 0) + 1
        }
        
        self._save()
    
    def is_first_analysis(self, repo_url: str) -> bool:
        """
        Check if this is the first time analyzing this repository
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            True if first analysis, False otherwise
        """
        repo_key = self._normalize_repo_url(repo_url)
        return repo_key not in self.data['repositories']
    
    def get_repo_info(self, repo_url: str) -> Optional[Dict]:
        """
        Get all stored information about a repository
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary with repo info or None
        """
        repo_key = self._normalize_repo_url(repo_url)
        return self.data['repositories'].get(repo_key)
    
    def get_all_repos(self) -> List[str]:
        """Get list of all tracked repositories"""
        return list(self.data['repositories'].keys())
    
    def clear_repo(self, repo_url: str):
        """Remove repository from tracking"""
        repo_key = self._normalize_repo_url(repo_url)
        if repo_key in self.data['repositories']:
            del self.data['repositories'][repo_key]
            self._save()