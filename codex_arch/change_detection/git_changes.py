"""
Git-based Change Detection System

This module provides functionality to detect changes between git commits using gitpython.
It identifies added, modified, and deleted files that may impact analysis artifacts.
"""

import os
import logging
from typing import Dict, List, Set, Tuple, Optional
from git import Repo, InvalidGitRepositoryError

logger = logging.getLogger(__name__)

class GitChangeDetector:
    """
    Detects changes between git commits or branches.
    
    This class uses gitpython to detect changes in a repository between commits,
    allowing for incremental analysis of only modified components.
    """
    
    def __init__(self, repo_path: str = '.'):
        """
        Initialize the GitChangeDetector.
        
        Args:
            repo_path: Path to the git repository. Defaults to current directory.
        
        Raises:
            InvalidGitRepositoryError: If the provided path is not a valid git repository.
        """
        try:
            self.repo = Repo(repo_path)
            self.repo_path = repo_path
            logger.info(f"Git repository initialized at {os.path.abspath(repo_path)}")
        except InvalidGitRepositoryError:
            logger.error(f"Invalid git repository: {os.path.abspath(repo_path)}")
            raise
    
    def get_changes(self, from_commit: str = 'HEAD~1', to_commit: str = 'HEAD') -> Dict[str, Set[str]]:
        """
        Get the files changed between two commits.
        
        Args:
            from_commit: The base commit to compare from. Defaults to the previous commit.
            to_commit: The target commit to compare to. Defaults to the current HEAD.
            
        Returns:
            Dictionary containing sets of added, modified, and deleted files.
        """
        try:
            # Get the diff between the two commits
            diff_index = self.repo.git.diff('--name-status', from_commit, to_commit)
            
            added_files = set()
            modified_files = set()
            deleted_files = set()
            
            # Parse the diff output
            if diff_index:
                for line in diff_index.split('\n'):
                    if not line.strip():
                        continue
                    
                    # The format is STATUS    FILENAME
                    parts = line.strip().split('\t')
                    if len(parts) < 2:
                        logger.warning(f"Unexpected diff format: {line}")
                        continue
                    
                    status, file_path = parts[0], parts[1]
                    
                    if status.startswith('A'):  # Added
                        added_files.add(file_path)
                    elif status.startswith('M'):  # Modified
                        modified_files.add(file_path)
                    elif status.startswith('D'):  # Deleted
                        deleted_files.add(file_path)
                    elif status.startswith('R'):  # Renamed
                        if len(parts) >= 3:  # Format: R{score}    old_name    new_name
                            deleted_files.add(parts[1])
                            added_files.add(parts[2])
                    
            logger.info(f"Detected changes: {len(added_files)} added, "
                        f"{len(modified_files)} modified, {len(deleted_files)} deleted")
            
            return {
                'added': added_files,
                'modified': modified_files,
                'deleted': deleted_files
            }
        except Exception as e:
            logger.error(f"Error getting changes between {from_commit} and {to_commit}: {str(e)}")
            return {'added': set(), 'modified': set(), 'deleted': set()}
    
    def detect_changes(self, from_commit: str = 'HEAD~1', to_commit: str = 'HEAD') -> Dict[str, Set[str]]:
        """
        Alias for get_changes() method to maintain backward compatibility.
        
        Args:
            from_commit: The base commit to compare from. Defaults to the previous commit.
            to_commit: The target commit to compare to. Defaults to the current HEAD.
            
        Returns:
            Dictionary containing sets of added, modified, and deleted files.
        """
        return self.get_changes(from_commit, to_commit)
    
    def get_affected_modules(self, changes: Dict[str, Set[str]], 
                             file_extensions: List[str] = None) -> Set[str]:
        """
        From a set of changed files, identify affected modules.
        
        Args:
            changes: Dictionary containing sets of added, modified, and deleted files.
            file_extensions: List of file extensions to filter by. If None, all files are included.
            
        Returns:
            Set of affected module names.
        """
        affected_modules = set()
        all_changes = set().union(
            changes.get('added', set()),
            changes.get('modified', set()),
            changes.get('deleted', set())
        )
        
        for file_path in all_changes:
            # Skip if the file doesn't match the extensions filter
            if file_extensions and not any(file_path.endswith(ext) for ext in file_extensions):
                continue
            
            # Extract module path from file path
            # For Python, we consider directories with __init__.py as modules
            module_path = os.path.dirname(file_path)
            if module_path:
                affected_modules.add(module_path)
            
            # The file itself may be a top-level module
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            if name_without_ext:
                affected_modules.add(name_without_ext)
        
        return affected_modules
    
    def has_changes(self) -> bool:
        """
        Check if there are any uncommitted changes in the repository.
        
        Returns:
            True if there are uncommitted changes, False otherwise.
        """
        return self.repo.is_dirty()
    
    def get_latest_commit_hash(self) -> str:
        """
        Get the hash of the latest commit.
        
        Returns:
            String hash of the latest commit.
        """
        return self.repo.head.commit.hexsha
    
    def get_commit_info(self, commit_hash: str = 'HEAD') -> Dict[str, str]:
        """
        Get information about a specific commit.
        
        Args:
            commit_hash: The hash of the commit to get info for. Defaults to HEAD.
            
        Returns:
            Dictionary with commit details.
        """
        commit = self.repo.commit(commit_hash)
        return {
            'hash': commit.hexsha,
            'author': f"{commit.author.name} <{commit.author.email}>",
            'date': commit.committed_datetime.isoformat(),
            'message': commit.message.strip()
        }
    
    def get_branch_name(self) -> Optional[str]:
        """
        Get the current branch name.
        
        Returns:
            String name of the current branch or None if in detached HEAD state.
        """
        try:
            return self.repo.active_branch.name
        except TypeError:  # Occurs in detached HEAD state
            return None 