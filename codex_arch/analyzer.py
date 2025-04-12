"""
Analyzer Module

This module provides functionality for analyzing code structure, dependencies,
complexity, and metrics across a codebase.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.extractors.file_tree_extractor import FileTreeExtractor

logger = logging.getLogger(__name__)

def run_analysis(
    paths: Union[str, List[str]],
    output_dir: Optional[str] = None,
    exclude_dirs: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    include_hidden: bool = False,
    incremental: bool = False,
    analyze_complexity: bool = True,
    analyze_dependencies: bool = True,
    analyze_metrics: bool = True,
) -> Dict[str, Any]:
    """
    Run analysis on the specified paths.
    
    Args:
        paths: Path or list of paths to analyze
        output_dir: Directory to store analysis output
        exclude_dirs: Directories to exclude
        exclude_patterns: Patterns to exclude
        include_hidden: Whether to include hidden files
        incremental: Whether this is an incremental analysis
        analyze_complexity: Whether to analyze code complexity
        analyze_dependencies: Whether to analyze dependencies
        analyze_metrics: Whether to analyze code metrics
        
    Returns:
        Dictionary containing analysis results
    """
    logger.info(f"Running analysis on {'multiple files' if isinstance(paths, list) else paths}")
    
    if isinstance(paths, str):
        paths = [paths]
    
    # Default exclude directories if none specified
    if exclude_dirs is None:
        exclude_dirs = ["venv", ".venv", "env", ".env", "node_modules", ".git", 
                        "__pycache__", ".pytest_cache", ".mypy_cache", ".coverage"]
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the results dictionary
    results = {
        "paths_analyzed": paths,
        "file_count": 0,
        "dependency_graph": {},
        "complexity_metrics": {},
        "file_metrics": {},
    }
    
    # Analyze metrics if requested
    if analyze_metrics:
        for path in paths:
            metrics_collector = MetricsCollector(
                root_path=path,
                exclude_dirs=exclude_dirs,
                exclude_patterns=exclude_patterns,
                include_hidden=include_hidden,
                analyze_complexity=analyze_complexity
            )
            metrics = metrics_collector.collect_metrics()
            results["file_metrics"][path] = metrics
            results["file_count"] += metrics.get("file_counts", {}).get("total", 0)
    
    # Extract file tree
    file_tree_extractor = FileTreeExtractor(
        root_path=paths[0] if len(paths) == 1 else os.getcwd(),
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns,
        include_hidden=include_hidden
    )
    file_tree = file_tree_extractor.extract()
    results["file_tree"] = file_tree
    
    # If only one path and it's a directory, update the full dependency graph
    if len(paths) == 1 and os.path.isdir(paths[0]):
        # For a directory, we create a placeholder dependency graph
        # In a real implementation, this would use language-specific extractors
        results["dependency_graph"] = {}
    
    logger.info(f"Analysis complete: {results['file_count']} files analyzed")
    
    # Output results if directory specified
    if output_dir:
        output_path = os.path.join(output_dir, "analysis_results.json")
        import json
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results written to {output_path}")
    
    return results 