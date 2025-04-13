"""
Storage Module

This module provides functionality for persistent storage and retrieval of analysis data.
It is used by the incremental analyzer to store and retrieve previous analysis results.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

logger = logging.getLogger(__name__)

class AnalysisStorage:
    """Storage class for analysis data."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the storage.
        
        Args:
            storage_dir: Directory to store analysis data. If None, uses .codex-arch in the repo root.
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".codex-arch")
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        self.analysis_file = self.storage_dir / "analysis.json"
        self.metadata_file = self.storage_dir / "metadata.json"
    
    def has_analysis_data(self) -> bool:
        """
        Check if analysis data exists.
        
        Returns:
            True if analysis data exists, False otherwise.
        """
        return self.analysis_file.exists()
    
    def get_analysis_data(self) -> Dict[str, Any]:
        """
        Get stored analysis data.
        
        Returns:
            Analysis data as a dictionary, or an empty dictionary if no data exists.
        """
        if not self.has_analysis_data():
            return {}
        
        try:
            with open(self.analysis_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading analysis data: {e}")
            return {}
    
    def update_analysis_data(self, analysis_data: Dict[str, Any]) -> None:
        """
        Update stored analysis data.
        
        Args:
            analysis_data: Analysis data to store.
        """
        # If existing data exists, merge with it
        if self.has_analysis_data():
            existing_data = self.get_analysis_data()
            # Merge the new data with existing data
            for key, value in analysis_data.items():
                if isinstance(value, dict) and key in existing_data and isinstance(existing_data[key], dict):
                    existing_data[key].update(value)
                else:
                    existing_data[key] = value
            merged_data = existing_data
        else:
            merged_data = analysis_data
        
        try:
            with open(self.analysis_file, 'w') as f:
                json.dump(merged_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing analysis data: {e}")
    
    def get_last_analyzed_commit(self) -> Optional[str]:
        """
        Get the hash of the last analyzed commit.
        
        Returns:
            The hash of the last analyzed commit, or None if not available.
        """
        if not self.metadata_file.exists():
            return None
        
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                return metadata.get('last_analyzed_commit')
        except Exception as e:
            logger.error(f"Error reading metadata: {e}")
            return None
    
    def set_last_analyzed_commit(self, commit_hash: str) -> None:
        """
        Set the hash of the last analyzed commit.
        
        Args:
            commit_hash: The hash of the commit to record.
        """
        metadata = {}
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error reading metadata: {e}")
        
        metadata['last_analyzed_commit'] = commit_hash
        
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing metadata: {e}")
    
    def get_dependency_graph(self) -> Optional[Dict[str, List[str]]]:
        """
        Get the stored dependency graph.
        
        Returns:
            The dependency graph, or None if not available.
        """
        analysis_data = self.get_analysis_data()
        return analysis_data.get('dependency_graph')

def get_storage(storage_dir: Optional[str] = None) -> AnalysisStorage:
    """
    Get a storage instance.
    
    Args:
        storage_dir: Directory to store analysis data. If None, uses .codex-arch in the repo root.
        
    Returns:
        An AnalysisStorage instance.
    """
    return AnalysisStorage(storage_dir) 