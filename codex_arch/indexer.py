"""
Indexer Module

This module provides functionality for indexing code repositories to enable
fast search and retrieval of code elements and their relationships.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

from codex_arch.storage import get_storage

logger = logging.getLogger(__name__)

def index_repository(
    repo_path: str,
    output_dir: Optional[str] = None,
    exclude_dirs: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    include_hidden: bool = False,
) -> Dict[str, Any]:
    """
    Index a code repository for faster searching and analysis.
    
    Args:
        repo_path: Path to the repository to index
        output_dir: Directory to store index output
        exclude_dirs: Directories to exclude
        exclude_patterns: Patterns to exclude
        include_hidden: Whether to include hidden files
        
    Returns:
        Dictionary containing indexing results
    """
    logger.info(f"Indexing repository: {repo_path}")
    
    # Default exclude directories if none specified
    if exclude_dirs is None:
        exclude_dirs = ["venv", ".venv", "env", ".env", "node_modules", ".git", 
                       "__pycache__", ".pytest_cache", ".mypy_cache", ".coverage"]
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the results dictionary
    results = {
        "repository": repo_path,
        "indexed_files": 0,
        "language_breakdown": {},
        "symbol_count": 0,
        "index_time": "",
    }
    
    # Get or create storage
    storage = get_storage(output_dir)
    
    # Prepare the file index
    file_index = {}
    symbol_index = {}
    
    # Walk the repository
    for root, dirs, files in os.walk(repo_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # Skip hidden files if requested
            if not include_hidden and file.startswith('.'):
                continue
                
            # Skip files matching exclude patterns
            skip = False
            if exclude_patterns:
                import re
                for pattern in exclude_patterns:
                    if re.search(pattern, file):
                        skip = True
                        break
            if skip:
                continue
                
            # Get the full file path
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Get file extension
            _, ext = os.path.splitext(file)
            if ext:
                ext = ext[1:]  # Remove the leading dot
            
            # Add file to index
            file_index[rel_path] = {
                "path": rel_path,
                "extension": ext,
                "size": os.path.getsize(file_path),
                "last_modified": os.path.getmtime(file_path),
            }
            
            # Update language breakdown
            if ext:
                results["language_breakdown"][ext] = results["language_breakdown"].get(ext, 0) + 1
    
    # Update results
    results["indexed_files"] = len(file_index)
    results["symbol_count"] = len(symbol_index)
    
    # Store the index
    index_data = {
        "metadata": results,
        "files": file_index,
        "symbols": symbol_index,
    }
    
    # Save to storage
    storage.update_analysis_data({"index": index_data})
    
    # Output results if directory specified
    if output_dir:
        output_path = os.path.join(output_dir, "index.json")
        with open(output_path, "w") as f:
            json.dump(index_data, f, indent=2)
        logger.info(f"Index written to {output_path}")
    
    logger.info(f"Indexing complete: {results['indexed_files']} files indexed")
    
    return results 