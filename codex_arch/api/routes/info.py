"""
Information routes for the Codex-Arch REST API.

These routes provide general information about the API and service.
"""

import os
import json
import platform
import logging
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app, g

from codex_arch.api.utils import (
    json_response, error_response, measure_execution_time
)
from codex_arch.api.cache.utils import invalidate_cache
from codex_arch.api.cache.stats import get_cache_stats, reset_cache_stats
from codex_arch.api.auth import admin_required, token_required
from codex_arch import __version__

# Create blueprint
bp = Blueprint('info', __name__)
logger = logging.getLogger(__name__)


@bp.route('/', methods=['GET'])
@measure_execution_time
def get_api_info():
    """Get general information about the API."""
    try:
        # Prepare response
        response_data = {
            'service': 'Codex-Arch API',
            'version': __version__,
            'status': 'operational',
            'api_version': current_app.config['API_VERSION'],
            'environment': os.environ.get('API_ENV', 'dev'),
            'endpoints': {
                'info': '/api/v1/info',
                'analysis': '/api/v1/analysis',
                'artifacts': '/api/v1/artifacts'
            }
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting API info: {str(e)}", exc_info=True)
        return error_response(f"Failed to get API info: {str(e)}", 500)


@bp.route('/endpoints', methods=['GET'])
@measure_execution_time
def get_endpoints():
    """Get information about available API endpoints."""
    try:
        # Define endpoints
        endpoints = {
            'info': {
                '/': {
                    'methods': ['GET'],
                    'description': 'Get general information about the API'
                },
                '/endpoints': {
                    'methods': ['GET'],
                    'description': 'Get information about available API endpoints'
                },
                '/system': {
                    'methods': ['GET'],
                    'description': 'Get system information'
                },
                '/cache': {
                    'methods': ['GET'],
                    'description': 'Get cache statistics (requires authentication)'
                },
                '/cache/reset': {
                    'methods': ['POST'],
                    'description': 'Reset cache statistics (requires admin authentication)'
                },
                '/cache/clear': {
                    'methods': ['POST'],
                    'description': 'Clear all caches (requires admin authentication)'
                }
            },
            'analysis': {
                '/file-tree': {
                    'methods': ['POST'],
                    'description': 'Extract and generate a file tree for a repository',
                    'body': {
                        'path': 'Path to the repository to analyze',
                        'include_patterns (optional)': 'Glob patterns for files to include',
                        'exclude_patterns (optional)': 'Glob patterns for files to exclude',
                        'output_format (optional)': 'Format for the output (json or markdown)',
                        'output_file (optional)': 'Output file path'
                    }
                },
                '/dependencies': {
                    'methods': ['POST'],
                    'description': 'Extract and analyze dependencies from Python code',
                    'body': {
                        'path': 'Path to the repository to analyze',
                        'include_patterns (optional)': 'Glob patterns for files to include',
                        'exclude_patterns (optional)': 'Glob patterns for files to exclude',
                        'output_dir (optional)': 'Output directory for results',
                        'output_file (optional)': 'Output filename'
                    }
                },
                '/metrics': {
                    'methods': ['POST'],
                    'description': 'Collect code metrics from a repository',
                    'body': {
                        'path': 'Path to the repository to analyze',
                        'include_patterns (optional)': 'Glob patterns for files to include',
                        'exclude_patterns (optional)': 'Glob patterns for files to exclude',
                        'output_dir (optional)': 'Output directory for results',
                        'output_file (optional)': 'Output filename'
                    }
                },
                '/full': {
                    'methods': ['POST'],
                    'description': 'Run a complete analysis pipeline on a repository',
                    'body': {
                        'path': 'Path to the repository to analyze',
                        'include_patterns (optional)': 'Glob patterns for files to include',
                        'exclude_patterns (optional)': 'Glob patterns for files to exclude',
                        'output_dir (optional)': 'Output directory for results',
                        'create_bundle (optional)': 'Whether to create a bundle'
                    }
                },
                '/status/<job_id>': {
                    'methods': ['GET'],
                    'description': 'Get the status of an analysis job'
                }
            },
            'artifacts': {
                '/list': {
                    'methods': ['GET'],
                    'description': 'List all artifacts in the output directory',
                    'query': {
                        'output_dir (optional)': 'Output directory to list artifacts from'
                    }
                },
                '/download/<artifact_path>': {
                    'methods': ['GET'],
                    'description': 'Download a specific artifact',
                    'query': {
                        'output_dir (optional)': 'Output directory to download from'
                    }
                },
                '/bundle/<job_id>': {
                    'methods': ['GET'],
                    'description': 'Download a generated bundle from a job'
                }
            }
        }
        
        # Initialize execution_times if it doesn't exist
        if not hasattr(g, 'execution_times'):
            g.execution_times = {}
        
        # Prepare response
        response_data = {
            'success': True,
            'api_version': current_app.config['API_VERSION'],
            'endpoints': endpoints,
            'execution_time': g.execution_times.get('get_endpoints', 0)
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting endpoints: {str(e)}", exc_info=True)
        return error_response(f"Failed to get endpoints: {str(e)}", 500)


@bp.route('/system', methods=['GET'])
@measure_execution_time
def get_system_info():
    """Get system information."""
    try:
        # Initialize execution_times if it doesn't exist
        if not hasattr(g, 'execution_times'):
            g.execution_times = {}
            
        # Prepare response
        response_data = {
            'success': True,
            'system': {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'platform_release': platform.release(),
                'python_version': platform.python_version(),
                'hostname': platform.node()
            },
            'execution_time': g.execution_times.get('get_system_info', 0)
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}", exc_info=True)
        return error_response(f"Failed to get system info: {str(e)}", 500)


@bp.route('/cache', methods=['GET'])
@token_required
@measure_execution_time
def get_cache_information():
    """
    Get cache statistics.
    
    Requires authentication.
    """
    try:
        # Get cache statistics
        cache_statistics = get_cache_stats()
        
        # Get cache configuration
        cache_config = {
            'cache_type': current_app.config['CACHE_TYPE'],
            'cache_default_timeout': current_app.config['CACHE_DEFAULT_TIMEOUT'],
            'disable_cache_in_debug': current_app.config.get('DISABLE_CACHE_IN_DEBUG', False)
        }
        
        # Add Redis configuration if relevant
        if current_app.config['CACHE_TYPE'] in ['RedisCache', 'RedisSentinelCache']:
            cache_config['redis_url'] = current_app.config.get('CACHE_REDIS_URL', 'not set')
            cache_config['redis_host'] = current_app.config['CACHE_OPTIONS'].get('CACHE_REDIS_HOST', 'localhost')
            cache_config['redis_port'] = current_app.config['CACHE_OPTIONS'].get('CACHE_REDIS_PORT', 6379)
            cache_config['redis_db'] = current_app.config['CACHE_OPTIONS'].get('CACHE_REDIS_DB', 0)
        
        # Prepare response
        response_data = {
            'success': True,
            'cache_statistics': cache_statistics,
            'cache_config': cache_config,
            'execution_time': g.execution_times.get('get_cache_information', 0)
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting cache info: {str(e)}", exc_info=True)
        return error_response(f"Failed to get cache info: {str(e)}", 500)


@bp.route('/cache/reset', methods=['POST'])
@token_required
@admin_required
@measure_execution_time
def reset_cache_statistics():
    """
    Reset cache statistics.
    
    Requires admin authentication.
    """
    try:
        # Reset cache statistics
        reset_cache_stats()
        
        # Prepare response
        response_data = {
            'success': True,
            'message': 'Cache statistics reset successfully',
            'execution_time': g.execution_times.get('reset_cache_statistics', 0)
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error resetting cache stats: {str(e)}", exc_info=True)
        return error_response(f"Failed to reset cache statistics: {str(e)}", 500)


@bp.route('/cache/clear', methods=['POST'])
@token_required
@admin_required
@measure_execution_time
def clear_all_caches():
    """
    Clear all caches.
    
    Requires admin authentication.
    """
    try:
        # Clear all caches
        namespaces = [
            'analysis_status', 'file_tree', 'dependencies', 
            'metrics', 'visualization', 'summary', 'artifacts_list'
        ]
        
        for namespace in namespaces:
            invalidate_cache(namespace)
        
        # Prepare response
        response_data = {
            'success': True,
            'message': 'All caches cleared successfully',
            'namespaces_cleared': namespaces,
            'execution_time': g.execution_times.get('clear_all_caches', 0)
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error clearing caches: {str(e)}", exc_info=True)
        return error_response(f"Failed to clear caches: {str(e)}", 500) 