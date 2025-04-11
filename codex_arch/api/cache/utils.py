"""
Cache utility functions for the Codex-Arch API.

Provides helper functions for caching and cache invalidation.
"""

import os
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from flask import request, current_app, g

from codex_arch.api.app import cache

logger = logging.getLogger(__name__)

def generate_cache_key(namespace: str, params: Dict[str, Any]) -> str:
    """
    Generate a deterministic cache key based on request parameters.
    
    Args:
        namespace: The namespace for the cache key (e.g., 'analysis')
        params: Dictionary of parameters to include in the key
        
    Returns:
        A unique cache key string
    """
    # Create a sorted, stringified version of the parameters
    param_str = json.dumps(params, sort_keys=True)
    
    # Generate a hash of the parameters
    param_hash = hashlib.md5(param_str.encode()).hexdigest()
    
    # Return a key with the namespace and hash
    return f"{namespace}:{param_hash}"


def cached_endpoint(namespace: str, params_extractor: Optional[Callable] = None, timeout: Optional[int] = None):
    """
    Decorator for caching API endpoint responses.
    
    Args:
        namespace: The namespace for the cache key (e.g., 'analysis')
        params_extractor: Function to extract cache key parameters from the request
        timeout: Cache timeout in seconds (None uses the default)
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip cache in debug mode if configured to do so
            if current_app.config.get('DEBUG') and current_app.config.get('DISABLE_CACHE_IN_DEBUG', False):
                return f(*args, **kwargs)
                
            # Extract parameters for the cache key
            if params_extractor:
                cache_params = params_extractor(request, *args, **kwargs)
            else:
                # Default extraction based on request data
                cache_params = {}
                
                # Include route parameters
                cache_params.update(kwargs)
                
                # Include query parameters
                cache_params.update(request.args.to_dict())
                
                # Include form and JSON data
                if request.is_json:
                    cache_params.update(request.get_json(silent=True) or {})
                elif request.form:
                    cache_params.update(request.form.to_dict())
            
            # Generate cache key
            cache_key = generate_cache_key(namespace, cache_params)
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {cache_key}")
                if hasattr(g, 'cache_hit'):
                    g.cache_hit = True
                return cached_response
                
            # Cache miss, execute the function
            logger.debug(f"Cache miss for {cache_key}")
            if hasattr(g, 'cache_hit'):
                g.cache_hit = False
                
            response = f(*args, **kwargs)
            
            # Cache the response
            actual_timeout = timeout or current_app.config.get('CACHE_DEFAULT_TIMEOUT')
            cache.set(cache_key, response, timeout=actual_timeout)
            
            return response
        return decorated_function
    return decorator


def invalidate_cache(namespace: str, pattern: Optional[str] = None):
    """
    Invalidate cache entries by namespace or pattern.
    
    Args:
        namespace: The namespace for the cache keys to invalidate
        pattern: Optional pattern to match cache keys (None invalidates all keys with the namespace)
    """
    if hasattr(cache, 'clear'):
        # For redis and other caches that support prefix-based deletion
        if pattern:
            cache_key_pattern = f"{namespace}:{pattern}"
        else:
            cache_key_pattern = f"{namespace}:*"
            
        # Clear matching keys
        try:
            # Try to use the cache's native pattern matching if available
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(cache_key_pattern)
            else:
                # If we're using SimpleCache, this won't work and will pass silently
                logger.warning("Current cache backend doesn't support pattern-based invalidation")
                # Fall back to clearing entire cache if using SimpleCache
                if cache.config['CACHE_TYPE'] == 'SimpleCache':
                    cache.clear()
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
    else:
        logger.warning("Cache backend doesn't support clearing")


def get_repo_cache_key(repo_path: str) -> str:
    """
    Generate a cache key for repository-related data.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        A unique cache key for the repository
    """
    # Use the absolute path as the basis for the key
    abs_path = os.path.abspath(repo_path)
    
    # Generate a hash of the path to avoid special characters
    path_hash = hashlib.md5(abs_path.encode()).hexdigest()
    
    return f"repo:{path_hash}"


def check_repo_modified(repo_path: str) -> bool:
    """
    Check if a repository has been modified since last cache.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if the repository has been modified, False otherwise
    """
    # In a real implementation, this would check Git status, file timestamps, etc.
    # For now, we'll use a simple check based on the most recent file modification time
    
    try:
        repo_key = get_repo_cache_key(repo_path)
        last_modified_cache = cache.get(f"{repo_key}:last_modified")
        
        if not last_modified_cache:
            # No cache entry, consider modified
            return True
            
        # Walk through the repository and find the most recent modification time
        most_recent_mod_time = 0
        for root, dirs, files in os.walk(repo_path):
            # Skip typical non-code directories
            if any(excluded in root for excluded in ['.git', '__pycache__', 'venv', 'node_modules']):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                mod_time = os.path.getmtime(file_path)
                most_recent_mod_time = max(most_recent_mod_time, mod_time)
        
        # Update the cache with the new modification time
        cache.set(f"{repo_key}:last_modified", most_recent_mod_time)
        
        # Check if the repository has been modified
        return most_recent_mod_time > last_modified_cache
        
    except Exception as e:
        logger.error(f"Error checking repository modifications: {str(e)}")
        # In case of error, assume modified to be safe
        return True


def update_repo_modified_time(repo_path: str):
    """
    Update the cached last modification time for a repository.
    
    Args:
        repo_path: Path to the repository
    """
    try:
        repo_key = get_repo_cache_key(repo_path)
        
        # Find the most recent modification time
        most_recent_mod_time = 0
        for root, dirs, files in os.walk(repo_path):
            # Skip typical non-code directories
            if any(excluded in root for excluded in ['.git', '__pycache__', 'venv', 'node_modules']):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                mod_time = os.path.getmtime(file_path)
                most_recent_mod_time = max(most_recent_mod_time, mod_time)
        
        # Update the cache
        cache.set(f"{repo_key}:last_modified", most_recent_mod_time)
        
    except Exception as e:
        logger.error(f"Error updating repository modification time: {str(e)}") 