"""
Cache statistics tracking for the Codex-Arch API.

Provides utilities for monitoring cache performance.
"""

import time
import logging
from typing import Dict, Any, Optional
from flask import g, request, current_app
from functools import wraps

logger = logging.getLogger(__name__)

# Global cache statistics
cache_stats = {
    'hits': 0,
    'misses': 0,
    'hit_ratio': 0.0,
    'endpoints': {}
}


def init_request_cache_tracking():
    """Initialize cache tracking for the current request."""
    g.cache_hit = None
    g.cache_start_time = time.time()


def track_cache_hit():
    """Track a cache hit."""
    if hasattr(g, 'cache_hit') and g.cache_hit is not None:
        endpoint = request.endpoint or 'unknown'
        
        # Update global stats
        if g.cache_hit:
            cache_stats['hits'] += 1
            if endpoint not in cache_stats['endpoints']:
                cache_stats['endpoints'][endpoint] = {'hits': 0, 'misses': 0, 'hit_ratio': 0.0}
            cache_stats['endpoints'][endpoint]['hits'] += 1
        else:
            cache_stats['misses'] += 1
            if endpoint not in cache_stats['endpoints']:
                cache_stats['endpoints'][endpoint] = {'hits': 0, 'misses': 0, 'hit_ratio': 0.0}
            cache_stats['endpoints'][endpoint]['misses'] += 1
        
        # Calculate hit ratios
        total = cache_stats['hits'] + cache_stats['misses']
        cache_stats['hit_ratio'] = cache_stats['hits'] / total if total > 0 else 0.0
        
        endpoint_total = cache_stats['endpoints'][endpoint]['hits'] + cache_stats['endpoints'][endpoint]['misses']
        if endpoint_total > 0:
            cache_stats['endpoints'][endpoint]['hit_ratio'] = (
                cache_stats['endpoints'][endpoint]['hits'] / endpoint_total
            )
        
        # Calculate time saved (if cache hit)
        if g.cache_hit and hasattr(g, 'cache_start_time') and hasattr(g, 'execution_times'):
            current_time = time.time()
            endpoint_name = request.endpoint.split('.')[-1] if request.endpoint else 'unknown'
            execution_time = g.execution_times.get(endpoint_name, 0)
            time_saved = execution_time - (current_time - g.cache_start_time)
            
            if time_saved > 0:
                if 'time_saved' not in cache_stats:
                    cache_stats['time_saved'] = 0.0
                cache_stats['time_saved'] += time_saved
                
                if 'time_saved' not in cache_stats['endpoints'][endpoint]:
                    cache_stats['endpoints'][endpoint]['time_saved'] = 0.0
                cache_stats['endpoints'][endpoint]['time_saved'] += time_saved


def track_cache_performance(f):
    """Decorator to track cache performance for an endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Initialize cache tracking
        init_request_cache_tracking()
        
        # Call the original function
        response = f(*args, **kwargs)
        
        # Track cache hit/miss and performance
        track_cache_hit()
        
        return response
    return decorated_function


def get_cache_stats() -> Dict[str, Any]:
    """
    Get the current cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    return {
        'hits': cache_stats['hits'],
        'misses': cache_stats['misses'],
        'hit_ratio': cache_stats['hit_ratio'],
        'time_saved': cache_stats.get('time_saved', 0.0),
        'endpoints': {
            endpoint: {
                'hits': stats['hits'],
                'misses': stats['misses'],
                'hit_ratio': stats['hit_ratio'],
                'time_saved': stats.get('time_saved', 0.0)
            }
            for endpoint, stats in cache_stats['endpoints'].items()
        }
    }


def reset_cache_stats():
    """Reset all cache statistics."""
    global cache_stats
    cache_stats = {
        'hits': 0,
        'misses': 0,
        'hit_ratio': 0.0,
        'time_saved': 0.0,
        'endpoints': {}
    } 