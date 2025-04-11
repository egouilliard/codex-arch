"""
Incremental Analysis Module

This module provides functionality to perform incremental analysis on code
based on Git changes, optimizing analysis time by only analyzing changed files.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union

from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.analyzer import run_analysis
from codex_arch.storage import get_storage

logger = logging.getLogger(__name__)


class IncrementalAnalyzer:
    """
    Performs incremental analysis on code changes.
    
    This analyzer optimizes analysis time by only analyzing files that have changed
    since the last analysis and their dependencies.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the incremental analyzer.
        
        Args:
            repo_path: Path to the repository to analyze.
        """
        self.repo_path = Path(repo_path)
        self.storage = get_storage()
        self.detector = GitChangeDetector(repo_path)
        
    def should_use_incremental(self) -> bool:
        """
        Determine if incremental analysis should be used.
        
        Returns:
            True if incremental analysis should be used, False if full analysis is needed.
        """
        # Check if we have a previous analysis to base incremental on
        return self.storage.has_analysis_data()
    
    def get_changed_files(self, from_commit: Optional[str] = None, 
                          to_commit: str = "HEAD") -> Dict[str, List[str]]:
        """
        Get files that have changed between two Git commits.
        
        Args:
            from_commit: Base commit for comparison. If None, uses the last analyzed commit.
            to_commit: Target commit for comparison. Defaults to HEAD.
            
        Returns:
            Dictionary with 'added', 'modified', and 'deleted' files.
        """
        # If no from_commit provided, try to get the last analyzed commit
        if from_commit is None:
            from_commit = self.storage.get_last_analyzed_commit()
            if from_commit is None:
                logger.warning("No previous analysis found, incremental analysis won't be effective")
                from_commit = "HEAD~10"  # Fallback to last 10 commits if no history
        
        return self.detector.get_changes(from_commit, to_commit)
    
    def get_dependency_impact(self, changed_files: Dict[str, List[str]]) -> Set[str]:
        """
        Calculate the impact of changed files on the dependency graph.
        
        Args:
            changed_files: Dictionary with 'added', 'modified', and 'deleted' files.
            
        Returns:
            Set of files that need to be reanalyzed due to direct changes or dependency changes.
        """
        # Get the current dependency graph
        dependency_graph = self.storage.get_dependency_graph() or {}
        
        # Files to reanalyze include all directly changed files
        files_to_reanalyze = set()
        for change_type in ["added", "modified"]:
            files_to_reanalyze.update(changed_files.get(change_type, []))
        
        # Now add any files that depend on changed files
        reverse_dependencies = self._build_reverse_dependency_graph(dependency_graph)
        
        # For each changed file, add all files that depend on it
        impacted_files = set(files_to_reanalyze)
        for changed_file in files_to_reanalyze:
            if changed_file in reverse_dependencies:
                impacted_files.update(reverse_dependencies[changed_file])
        
        return impacted_files
    
    def _build_reverse_dependency_graph(self, 
                                       dependency_graph: Dict[str, List[str]]) -> Dict[str, Set[str]]:
        """
        Build a reverse dependency graph.
        
        Args:
            dependency_graph: The forward dependency graph.
            
        Returns:
            A dictionary mapping files to the set of files that depend on them.
        """
        reverse_graph: Dict[str, Set[str]] = {}
        
        for file, dependencies in dependency_graph.items():
            for dependency in dependencies:
                if dependency not in reverse_graph:
                    reverse_graph[dependency] = set()
                reverse_graph[dependency].add(file)
        
        return reverse_graph
    
    def perform_incremental_dependency_analysis(self, 
                                               from_commit: Optional[str] = None,
                                               to_commit: str = "HEAD") -> Dict[str, Any]:
        """
        Perform incremental dependency analysis based on Git changes.
        
        Args:
            from_commit: Base commit for comparison. If None, uses the last analyzed commit.
            to_commit: Target commit for comparison. Defaults to HEAD.
            
        Returns:
            Analysis results.
        """
        # Get changed files
        changed_files = self.get_changed_files(from_commit, to_commit)
        
        # If no changes, return early
        if not any(changed_files.values()):
            logger.info("No changes detected, skipping analysis")
            return {}
        
        # Calculate which files need to be reanalyzed
        files_to_analyze = self.get_dependency_impact(changed_files)
        
        if not files_to_analyze:
            logger.info("No files to analyze")
            return {}
            
        logger.info(f"Performing incremental analysis on {len(files_to_analyze)} files")
        
        # Perform analysis on the impacted files
        analysis_results = run_analysis(
            paths=list(files_to_analyze),
            incremental=True
        )
        
        # Update the storage with the latest analysis
        self.storage.update_analysis_data(analysis_results)
        self.storage.set_last_analyzed_commit(to_commit)
        
        return analysis_results
    
    def perform_incremental_metrics_analysis(self,
                                           from_commit: Optional[str] = None,
                                           to_commit: str = "HEAD") -> Dict[str, Any]:
        """
        Perform incremental metrics analysis based on Git changes.
        
        This is a lighter-weight analysis focused on code metrics rather than
        full dependency analysis, suitable for pre-push hooks.
        
        Args:
            from_commit: Base commit for comparison. If None, uses the last analyzed commit.
            to_commit: Target commit for comparison. Defaults to HEAD.
            
        Returns:
            Metrics analysis results.
        """
        # Get changed files
        changed_files = self.get_changed_files(from_commit, to_commit)
        
        # Only analyze added and modified files
        files_to_analyze = []
        for change_type in ["added", "modified"]:
            files_to_analyze.extend(changed_files.get(change_type, []))
        
        if not files_to_analyze:
            logger.info("No files to analyze for metrics")
            return {}
            
        logger.info(f"Performing metrics analysis on {len(files_to_analyze)} files")
        
        # Perform lightweight metrics analysis
        metrics_results = {
            'file_metrics': {}
        }
        
        # Placeholder for actual metrics analysis
        # In a real implementation, you would call specific metrics analyzers
        # For now, we'll just count lines of code as a simple metric
        for file_path in files_to_analyze:
            full_path = self.repo_path / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.readlines()
                    metrics_results['file_metrics'][file_path] = {
                        'loc': len(content),
                        'complexity': len(content) // 10  # Dummy complexity metric
                    }
                except Exception as e:
                    logger.warning(f"Error analyzing metrics for {file_path}: {str(e)}")
        
        return metrics_results 