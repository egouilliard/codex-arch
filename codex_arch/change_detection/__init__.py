"""
Change Detection Module

This module provides functionality to detect changes in the repository and enables
incremental updates to analysis artifacts.
"""

from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.change_detection.caching import CacheManager
from codex_arch.change_detection.incremental import IncrementalAnalyzer
from codex_arch.change_detection.summary import ChangeSummaryGenerator

__all__ = [
    'GitChangeDetector',
    'CacheManager',
    'IncrementalAnalyzer',
    'ChangeSummaryGenerator',
    'detect_changes',
    'summarize_changes',
]

def detect_changes(repo_path, from_commit=None, to_commit='HEAD'):
    """
    Detect changes between Git commits.
    
    Args:
        repo_path: Path to the Git repository
        from_commit: Base commit for comparison. If None, uses the last analyzed commit.
        to_commit: Target commit for comparison.
        
    Returns:
        Dictionary with 'added', 'modified', and 'deleted' files.
    """
    detector = GitChangeDetector(repo_path)
    return detector.get_changes(from_commit, to_commit)

def summarize_changes(repo_path, from_commit=None, to_commit='HEAD'):
    """
    Summarize changes between Git commits.
    
    Args:
        repo_path: Path to the Git repository
        from_commit: Base commit for comparison. If None, uses the last analyzed commit.
        to_commit: Target commit for comparison.
        
    Returns:
        Dictionary with summary metrics about the changes.
    """
    summary_generator = ChangeSummaryGenerator(repo_path)
    return summary_generator.generate_summary(from_commit, to_commit) 