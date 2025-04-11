"""
Incremental Analysis Updates Module

This module provides functionality to perform incremental updates to analysis
artifacts based on detected changes, avoiding full reanalysis where possible.
"""

import os
import logging
import json
from typing import Dict, List, Set, Any, Optional, Tuple

from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.change_detection.caching import CacheManager
from codex_arch.extractors.python import dependency_analyzer
from codex_arch.metrics import metrics_collector
from codex_arch.visualization.graph import dependency_graph_generator

logger = logging.getLogger(__name__)

class IncrementalAnalyzer:
    """
    Performs incremental updates to analysis artifacts.
    
    This class uses change detection and caching to update only affected parts
    of the analysis, improving performance for large codebases.
    """
    
    def __init__(self, repo_path: str = '.', cache_dir: str = '.codex_cache'):
        """
        Initialize the IncrementalAnalyzer.
        
        Args:
            repo_path: Path to the git repository. Defaults to current directory.
            cache_dir: Directory where cache files are stored. Defaults to '.codex_cache'.
        """
        self.repo_path = repo_path
        self.git_detector = GitChangeDetector(repo_path)
        self.cache_manager = CacheManager(cache_dir=cache_dir)
        
    def should_use_incremental(self, force_full: bool = False) -> bool:
        """
        Determine if incremental analysis should be used.
        
        Args:
            force_full: If True, always performs full analysis. Defaults to False.
            
        Returns:
            True if incremental analysis should be used, False otherwise.
        """
        if force_full:
            return False
            
        # Check if this is the first run (no cache)
        cache_keys = self.cache_manager.get_cache_keys()
        if not cache_keys:
            logger.info("No cache found, performing full analysis")
            return False
            
        # Check if there are any changes
        try:
            last_commit_hash = self.git_detector.get_latest_commit_hash()
            changes = self.git_detector.get_changes()
            if not any(changes.values()):
                logger.info("No changes detected, using cached results")
                return True
                
            # Check if we have more than a threshold of changes
            # If too many files changed, it might be faster to do a full analysis
            all_changed_files = set().union(*changes.values())
            if len(all_changed_files) > 100:  # Arbitrary threshold
                logger.info(f"Too many changes ({len(all_changed_files)} files), performing full analysis")
                return False
                
            return True
        except Exception as e:
            logger.warning(f"Error determining analysis mode: {str(e)}")
            return False
    
    def perform_incremental_dependency_analysis(self, 
                                               from_commit: str = 'HEAD~1', 
                                               to_commit: str = 'HEAD',
                                               python_files_only: bool = True) -> Dict[str, Any]:
        """
        Perform incremental dependency analysis based on changes.
        
        Args:
            from_commit: The base commit to compare from. Defaults to the previous commit.
            to_commit: The target commit to compare to. Defaults to the current HEAD.
            python_files_only: If True, only analyzes Python files. Defaults to True.
            
        Returns:
            Updated dependency analysis results.
        """
        logger.info(f"Performing incremental dependency analysis from {from_commit} to {to_commit}")
        
        # Get changes between commits
        changes = self.git_detector.get_changes(from_commit, to_commit)
        
        # Filter to only include Python files if specified
        if python_files_only:
            for change_type in changes:
                changes[change_type] = {file for file in changes[change_type] if file.endswith('.py')}
        
        # Get cached full dependency analysis if it exists
        commit_hash = self.git_detector.get_latest_commit_hash()
        cached_analysis = self.cache_manager.get_cached_result_for_commit('deps_analysis', commit_hash)
        
        if not cached_analysis:
            # No cache for the latest commit, look for cache from the previous commit
            prev_commit_hash = from_commit
            cached_analysis = self.cache_manager.get_cached_result_for_commit('deps_analysis', prev_commit_hash)
            
            if not cached_analysis:
                # No previous analysis found, perform full analysis
                logger.info("No cached analysis found, performing full analysis")
                return self._perform_full_dependency_analysis(to_commit)
        
        # We have a cached analysis, now apply incremental updates
        updated_analysis = self._update_dependency_analysis(cached_analysis, changes)
        
        # Save the updated analysis to cache
        cache_key = self.cache_manager.generate_cache_key('deps_analysis', commit_hash)
        self.cache_manager.set_cache_entry(cache_key, updated_analysis, commit_hash)
        
        return updated_analysis
    
    def _perform_full_dependency_analysis(self, commit: str = 'HEAD') -> Dict[str, Any]:
        """
        Perform a full dependency analysis.
        
        Args:
            commit: The commit to analyze. Defaults to HEAD.
            
        Returns:
            Results of the full dependency analysis.
        """
        logger.info(f"Performing full dependency analysis for commit {commit}")
        
        # Here we would call the full dependency analysis functions
        # This is just a placeholder - you would integrate with your actual analyzer
        analyzer = dependency_analyzer.DependencyAnalyzer(self.repo_path)
        full_analysis = analyzer.analyze_dependencies()
        
        # Cache the results
        commit_hash = self.git_detector.get_latest_commit_hash()
        cache_key = self.cache_manager.generate_cache_key('deps_analysis', commit_hash)
        self.cache_manager.set_cache_entry(cache_key, full_analysis, commit_hash)
        
        return full_analysis
    
    def _update_dependency_analysis(self, 
                                   cached_analysis: Dict[str, Any], 
                                   changes: Dict[str, Set[str]]) -> Dict[str, Any]:
        """
        Update dependency analysis based on file changes.
        
        Args:
            cached_analysis: The previous dependency analysis results.
            changes: Dictionary of file changes (added, modified, deleted).
            
        Returns:
            Updated dependency analysis.
        """
        logger.info("Updating dependency analysis with changes")
        
        # Clone the cached analysis to avoid modifying the original
        updated_analysis = json.loads(json.dumps(cached_analysis))
        
        # Convert file paths to module names for easier reference
        affected_modules = self.git_detector.get_affected_modules(changes, file_extensions=['.py'])
        
        # Handle deleted files/modules
        for file_path in changes.get('deleted', set()):
            module_name = self._file_path_to_module_name(file_path)
            if module_name in updated_analysis.get('dependencies', {}):
                logger.info(f"Removing module from analysis: {module_name}")
                del updated_analysis['dependencies'][module_name]
        
        # Handle added and modified files
        combined_changes = changes.get('added', set()).union(changes.get('modified', set()))
        if combined_changes:
            # Analyze only the changed files
            analyzer = dependency_analyzer.DependencyAnalyzer(self.repo_path)
            partial_analysis = analyzer.analyze_specific_files(list(combined_changes))
            
            # Merge the partial analysis with the cached one
            for module, deps in partial_analysis.get('dependencies', {}).items():
                updated_analysis['dependencies'][module] = deps
        
        # Update any metrics or statistics
        self._recalculate_metrics(updated_analysis)
        
        return updated_analysis
    
    def _file_path_to_module_name(self, file_path: str) -> str:
        """
        Convert a file path to a Python module name.
        
        Args:
            file_path: Path to the Python file.
            
        Returns:
            Python module name.
        """
        if not file_path.endswith('.py'):
            return file_path
            
        # Remove .py extension
        module_path = file_path[:-3]
        # Replace directory separators with dots
        module_name = module_path.replace('/', '.').replace('\\', '.')
        # Remove __init__ from the end if present
        if module_name.endswith('.__init__'):
            module_name = module_name[:-9]
            
        return module_name
    
    def _recalculate_metrics(self, analysis: Dict[str, Any]) -> None:
        """
        Recalculate metrics based on updated dependencies.
        
        Args:
            analysis: The dependency analysis to update metrics for.
        """
        # Example metrics: module count, dependency count, etc.
        modules = analysis.get('dependencies', {})
        
        metrics = {
            'module_count': len(modules),
            'total_dependencies': sum(len(deps) for deps in modules.values()),
            'last_updated': self.git_detector.get_commit_info()
        }
        
        analysis['metrics'] = metrics
    
    def perform_incremental_metrics_analysis(self, 
                                            from_commit: str = 'HEAD~1', 
                                            to_commit: str = 'HEAD') -> Dict[str, Any]:
        """
        Perform incremental metrics analysis.
        
        Args:
            from_commit: The base commit to compare from. Defaults to the previous commit.
            to_commit: The target commit to compare to. Defaults to the current HEAD.
            
        Returns:
            Updated metrics analysis results.
        """
        logger.info(f"Performing incremental metrics analysis from {from_commit} to {to_commit}")
        
        # Get changed files
        changes = self.git_detector.get_changes(from_commit, to_commit)
        all_changed_files = set().union(*changes.values())
        
        # Get cached metrics if they exist
        commit_hash = self.git_detector.get_latest_commit_hash()
        cached_metrics = self.cache_manager.get_cached_result_for_commit('metrics_analysis', commit_hash)
        
        if not cached_metrics or not all_changed_files:
            # If no cache or no changes, perform full analysis
            return self._perform_full_metrics_analysis()
        
        # Update metrics for changed files
        updated_metrics = self._update_metrics_analysis(cached_metrics, all_changed_files)
        
        # Save updated metrics to cache
        cache_key = self.cache_manager.generate_cache_key('metrics_analysis', commit_hash)
        self.cache_manager.set_cache_entry(cache_key, updated_metrics, commit_hash)
        
        return updated_metrics
    
    def _perform_full_metrics_analysis(self) -> Dict[str, Any]:
        """
        Perform a full metrics analysis.
        
        Returns:
            Results of the full metrics analysis.
        """
        logger.info("Performing full metrics analysis")
        
        # Here we would call the metrics collector
        metrics = metrics_collector.collect_metrics(self.repo_path)
        
        # Cache the results
        commit_hash = self.git_detector.get_latest_commit_hash()
        cache_key = self.cache_manager.generate_cache_key('metrics_analysis', commit_hash)
        self.cache_manager.set_cache_entry(cache_key, metrics, commit_hash)
        
        return metrics
    
    def _update_metrics_analysis(self, 
                                cached_metrics: Dict[str, Any], 
                                changed_files: Set[str]) -> Dict[str, Any]:
        """
        Update metrics analysis based on changed files.
        
        Args:
            cached_metrics: The previous metrics results.
            changed_files: Set of files that have changed.
            
        Returns:
            Updated metrics analysis.
        """
        logger.info(f"Updating metrics for {len(changed_files)} changed files")
        
        # Clone the cached metrics to avoid modifying the original
        updated_metrics = json.loads(json.dumps(cached_metrics))
        
        # Recalculate metrics only for changed files
        collector = metrics_collector.MetricsCollector()
        partial_metrics = collector.collect_metrics_for_files(list(changed_files))
        
        # Update file-specific metrics
        file_metrics = updated_metrics.get('file_metrics', {})
        for file_path, metrics in partial_metrics.get('file_metrics', {}).items():
            file_metrics[file_path] = metrics
        
        # Update removed files
        for file_path in changed_files:
            if file_path in changed_files and file_path not in partial_metrics.get('file_metrics', {}):
                if file_path in file_metrics:
                    del file_metrics[file_path]
        
        updated_metrics['file_metrics'] = file_metrics
        
        # Recalculate aggregated metrics
        self._recalculate_aggregated_metrics(updated_metrics)
        
        return updated_metrics
    
    def _recalculate_aggregated_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Recalculate aggregated metrics from file-specific metrics.
        
        Args:
            metrics: The metrics dictionary to update.
        """
        file_metrics = metrics.get('file_metrics', {})
        
        # Example aggregation: total lines of code
        total_loc = sum(m.get('loc', 0) for m in file_metrics.values())
        total_files = len(file_metrics)
        
        aggregated = {
            'total_files': total_files,
            'total_loc': total_loc,
            'avg_loc_per_file': total_loc / total_files if total_files > 0 else 0,
            'last_updated': self.git_detector.get_commit_info()
        }
        
        metrics['aggregated'] = aggregated
    
    def update_visualization(self, 
                            dependency_analysis: Dict[str, Any], 
                            output_file: str = 'dependency_graph.svg') -> bool:
        """
        Update visualization based on dependency analysis.
        
        Args:
            dependency_analysis: The dependency analysis results to visualize.
            output_file: Path to the output visualization file. Defaults to 'dependency_graph.svg'.
            
        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Updating visualization to {output_file}")
        
        try:
            # Generate visualization using the graph generator
            generator = dependency_graph_generator.DependencyGraphGenerator()
            generator.generate(dependency_analysis, output_file)
            return True
        except Exception as e:
            logger.error(f"Error updating visualization: {str(e)}")
            return False 