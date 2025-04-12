"""
Caching System for Analysis Results

This module implements a caching system that stores previous analysis results,
allowing for incremental updates and avoiding redundant calculations.
"""

import os
import json
import hashlib
import logging
import time
from typing import Dict, Any, Optional, List, Set

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages caching of analysis results.
    
    This class provides functionality to store and retrieve analysis results,
    enabling incremental analysis with appropriate cache invalidation strategies.
    """
    
    def __init__(self, cache_dir: str = '.codex_cache', cache_filename: str = 'deps_cache.json'):
        """
        Initialize the CacheManager.
        
        Args:
            cache_dir: Directory where cache files are stored. Defaults to '.codex_cache'.
            cache_filename: Name of the main cache file. Defaults to 'deps_cache.json'.
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, cache_filename)
        self.cache_data = {}
        self._ensure_cache_dir()
        self._load_cache()
    
    def _ensure_cache_dir(self) -> None:
        """Create the cache directory if it doesn't exist."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"Created cache directory: {self.cache_dir}")
    
    def _load_cache(self) -> None:
        """Load cache data from the cache file if it exists."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                logger.info(f"Loaded cache from {self.cache_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache: {str(e)}")
                self.cache_data = {}
        else:
            logger.info(f"No cache file found at {self.cache_file}")
            self.cache_data = {}
    
    def _save_cache(self) -> None:
        """Save cache data to the cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
            logger.info(f"Saved cache to {self.cache_file}")
        except IOError as e:
            logger.error(f"Failed to save cache: {str(e)}")
    
    def get_cache_entry(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a cache entry by key.
        
        Args:
            key: The cache key to retrieve.
            
        Returns:
            The cached data or None if not found.
        """
        return self.cache_data.get(key)
    
    def set_cache_entry(self, key: str, data: Dict[str, Any], commit_hash: str = None,
                       metadata: Dict[str, Any] = None) -> None:
        """
        Set a cache entry.
        
        Args:
            key: The cache key to set.
            data: The data to cache.
            commit_hash: Git commit hash associated with this cache entry.
            metadata: Additional metadata to store with the cache entry.
        """
        entry = {
            'data': data,
            'timestamp': time.time(),
            'commit_hash': commit_hash,
            'metadata': metadata or {}
        }
        self.cache_data[key] = entry
        self._save_cache()
    
    def invalidate_cache_entry(self, key: str) -> bool:
        """
        Invalidate (remove) a cache entry.
        
        Args:
            key: The cache key to invalidate.
            
        Returns:
            True if the entry was removed, False if it didn't exist.
        """
        if key in self.cache_data:
            del self.cache_data[key]
            self._save_cache()
            logger.info(f"Invalidated cache entry: {key}")
            return True
        return False
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        self.cache_data = {}
        self._save_cache()
        logger.info("Cleared all cache entries")
    
    def get_cache_keys(self) -> List[str]:
        """
        Get a list of all cache keys.
        
        Returns:
            List of all cache keys.
        """
        return list(self.cache_data.keys())
    
    def compute_file_hash(self, file_path: str) -> Optional[str]:
        """
        Compute an MD5 hash of a file's contents.
        
        Args:
            file_path: Path to the file to hash.
            
        Returns:
            MD5 hash as a hex string or None if the file doesn't exist.
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except IOError as e:
            logger.error(f"Failed to hash file {file_path}: {str(e)}")
            return None
    
    def is_cache_valid(self, key: str, file_hashes: Dict[str, str] = None) -> bool:
        """
        Check if a cache entry is valid based on file hashes.
        
        Args:
            key: The cache key to check.
            file_hashes: Dictionary mapping file paths to their expected hash values.
                         If provided, the cache is valid only if all files match their hash.
            
        Returns:
            True if the cache entry is valid, False otherwise.
        """
        if key not in self.cache_data:
            return False
        
        # If no file hashes provided, just check if the key exists
        if not file_hashes:
            return True
        
        # Check if all files match their expected hash
        cache_entry = self.cache_data[key]
        stored_hashes = cache_entry.get('metadata', {}).get('file_hashes', {})
        
        for file_path, expected_hash in file_hashes.items():
            if stored_hashes.get(file_path) != expected_hash:
                return False
                
        return True
    
    def get_file_hash_for_files(self, file_paths: List[str]) -> Dict[str, str]:
        """
        Compute hashes for multiple files.
        
        Args:
            file_paths: List of file paths to compute hashes for.
            
        Returns:
            Dictionary mapping file paths to their hash values.
        """
        result = {}
        for file_path in file_paths:
            file_hash = self.compute_file_hash(file_path)
            if file_hash:
                result[file_path] = file_hash
        return result
    
    def generate_cache_key(self, prefix: str, commit_hash: str = None, 
                          file_paths: List[str] = None) -> str:
        """
        Generate a cache key based on prefix, commit hash, and file paths.
        
        Args:
            prefix: Prefix for the cache key.
            commit_hash: Git commit hash to include in the key.
            file_paths: List of file paths to include in the key.
            
        Returns:
            Generated cache key.
        """
        components = [prefix]
        
        if commit_hash:
            components.append(f"commit_{commit_hash[:8]}")
        
        if file_paths:
            # Sort to ensure consistent key generation
            file_paths = sorted(file_paths)
            # Use a hash of the file paths to keep the key manageable
            paths_str = ";".join(file_paths)
            paths_hash = hashlib.md5(paths_str.encode()).hexdigest()[:8]
            components.append(f"files_{paths_hash}")
        
        return "_".join(components)
    
    def get_cached_result_for_commit(self, prefix: str, commit_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for a specific commit.
        
        Args:
            prefix: Prefix for the cache key.
            commit_hash: Git commit hash to find in the cache.
            
        Returns:
            Cached data or None if not found.
        """
        # Try to find a cache entry with matching commit hash
        for key, entry in self.cache_data.items():
            if key.startswith(prefix) and entry.get('commit_hash') == commit_hash:
                return entry.get('data')
        return None 