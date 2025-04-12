"""
Query Module

This module provides functionality for querying code architecture data
to retrieve information about code elements and their relationships.
"""

import os
import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

from codex_arch.storage import get_storage

logger = logging.getLogger(__name__)

def query_architecture(
    query: str,
    repo_path: Optional[str] = None,
    query_type: str = "general",
    output_file: Optional[str] = None,
    max_results: int = 100,
    include_code: bool = False,
) -> Dict[str, Any]:
    """
    Query code architecture data.
    
    Args:
        query: The query string
        repo_path: Path to the repository to query
        query_type: Type of query (general, file, symbol, dependency)
        output_file: File to save results to
        max_results: Maximum number of results to return
        include_code: Whether to include code snippets in results
        
    Returns:
        Dictionary containing query results
    """
    logger.info(f"Querying architecture with query: {query}")
    
    # Initialize the storage
    storage = get_storage()
    
    # Get the stored analysis data
    analysis_data = storage.get_analysis_data()
    
    # Initialize results
    results = {
        "query": query,
        "query_type": query_type,
        "total_matches": 0,
        "matches": [],
    }
    
    # If there's no analysis data, return empty results
    if not analysis_data:
        logger.warning("No analysis data found for querying")
        return results
    
    # Get index data if it exists
    index_data = analysis_data.get("index", {})
    files = index_data.get("files", {})
    
    # Process query based on type
    if query_type == "file":
        # Query for files matching pattern
        matches = []
        for file_path, file_info in files.items():
            if re.search(query, file_path, re.IGNORECASE):
                matches.append(file_info)
                
        results["matches"] = matches[:max_results]
        results["total_matches"] = len(matches)
    
    elif query_type == "symbol":
        # Query for symbols matching pattern
        symbols = index_data.get("symbols", {})
        matches = []
        for symbol, symbol_info in symbols.items():
            if re.search(query, symbol, re.IGNORECASE):
                matches.append(symbol_info)
                
        results["matches"] = matches[:max_results]
        results["total_matches"] = len(matches)
    
    elif query_type == "dependency":
        # Query for dependencies matching pattern
        dependency_graph = analysis_data.get("dependency_graph", {})
        matches = []
        
        for source, targets in dependency_graph.items():
            if re.search(query, source, re.IGNORECASE):
                matches.append({
                    "source": source,
                    "targets": targets
                })
            else:
                for target in targets:
                    if re.search(query, target, re.IGNORECASE):
                        matches.append({
                            "source": source,
                            "targets": targets
                        })
                        break
                
        results["matches"] = matches[:max_results]
        results["total_matches"] = len(matches)
    
    else:  # General query
        # Query across all data types
        file_matches = []
        for file_path, file_info in files.items():
            if re.search(query, file_path, re.IGNORECASE):
                file_matches.append(file_info)
        
        symbols = index_data.get("symbols", {})
        symbol_matches = []
        for symbol, symbol_info in symbols.items():
            if re.search(query, symbol, re.IGNORECASE):
                symbol_matches.append(symbol_info)
        
        results["matches"] = {
            "files": file_matches[:max_results],
            "symbols": symbol_matches[:max_results],
        }
        results["total_matches"] = len(file_matches) + len(symbol_matches)
    
    # Include code snippets if requested
    if include_code and repo_path and results["matches"]:
        if query_type == "file" or query_type == "general":
            for match in (results["matches"] if query_type == "file" else results["matches"]["files"]):
                file_path = match.get("path")
                if file_path:
                    full_path = os.path.join(repo_path, file_path)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            match["preview"] = f.read(500)  # Read first 500 chars
                    except Exception as e:
                        logger.error(f"Failed to read file for preview: {e}")
    
    # Output results if file specified
    if output_file:
        try:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            logger.info(f"Query results written to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write query results: {e}")
    
    logger.info(f"Query complete: {results['total_matches']} matches found")
    
    return results 