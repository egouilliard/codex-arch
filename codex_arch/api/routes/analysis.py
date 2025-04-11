"""
Analysis routes for the Codex-Arch REST API.

These routes handle triggering and managing code analysis operations.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app, abort, g
from werkzeug.utils import secure_filename

from codex_arch.api.utils import (
    json_response, error_response, validate_path, 
    measure_execution_time, generate_unique_id, save_uploaded_file
)
from codex_arch.api.cache.utils import (
    cached_endpoint, check_repo_modified, update_repo_modified_time,
    invalidate_cache, get_repo_cache_key
)
from codex_arch.extractors.file_tree_extractor import FileTreeExtractor
from codex_arch.extractors.python.extractor import PythonDependencyExtractor
from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.visualization.graph.dot_generator import DotGenerator
from codex_arch.summary.data_collector import DataCollector
from codex_arch.bundler.context_bundle_assembler import ContextBundleAssembler, BundleConfig

# Create blueprint
bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)

# In-memory job status storage (in a real app, use a database)
analysis_jobs = {}


@bp.route('/status/<job_id>', methods=['GET'])
@cached_endpoint('analysis_status')
def get_job_status(job_id):
    """Get the status of an analysis job."""
    if job_id not in analysis_jobs:
        return error_response(f"Job ID {job_id} not found", 404)
    
    return json_response(analysis_jobs[job_id])


def file_tree_params_extractor(request, *args, **kwargs):
    """Extract cache key parameters for file tree analysis."""
    params = {}
    if request.is_json:
        data = request.get_json()
        params['path'] = data.get('path')
        params['include_patterns'] = sorted(data.get('include_patterns', ['**/*']))
        params['exclude_patterns'] = sorted(data.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**']))
        params['output_format'] = data.get('output_format', 'json')
    return params


@bp.route('/file-tree', methods=['POST'])
@measure_execution_time
@cached_endpoint('file_tree', params_extractor=file_tree_params_extractor)
def analyze_file_tree():
    """Extract and generate a file tree for a repository."""
    if not request.json or 'path' not in request.json:
        return error_response("Missing required parameter: 'path'")
    
    repo_path = request.json['path']
    if not validate_path(repo_path):
        return error_response(f"Invalid or inaccessible path: {repo_path}")
    
    # Check if repository has been modified since last cache
    if check_repo_modified(repo_path):
        # If repository was modified, invalidate all related caches
        repo_key = get_repo_cache_key(repo_path)
        invalidate_cache('file_tree', repo_key)
    
    try:
        # Get optional parameters
        include_patterns = request.json.get('include_patterns', ['**/*'])
        exclude_patterns = request.json.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**'])
        output_format = request.json.get('output_format', 'json')
        output_file = request.json.get('output_file')
        
        # Initialize extractor
        extractor = FileTreeExtractor(
            repo_path, 
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        # Extract file tree
        file_tree = extractor.extract()
        
        # Generate output
        if output_format == 'json':
            result = extractor.to_json(output_file)
        else:  # markdown
            result = extractor.to_markdown(output_file)
        
        # Prepare response
        output_path = None
        if output_file:
            output_path = os.path.abspath(output_file)
        
        response_data = {
            'success': True,
            'repo_path': repo_path,
            'file_count': len(extractor.get_all_files()),
            'directory_count': len(extractor.get_all_directories()),
            'output_format': output_format,
            'output_path': output_path,
            'execution_time': g.execution_times.get('analyze_file_tree', 0)
        }
        
        if not output_file:
            response_data['result'] = result
        
        # Update repository modified time after successful analysis
        update_repo_modified_time(repo_path)
            
        return json_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in file tree analysis: {str(e)}", exc_info=True)
        return error_response(f"Analysis failed: {str(e)}", 500)


def dependencies_params_extractor(request, *args, **kwargs):
    """Extract cache key parameters for dependencies analysis."""
    params = {}
    if request.is_json:
        data = request.get_json()
        params['path'] = data.get('path')
        params['include_patterns'] = sorted(data.get('include_patterns', ['**/*.py']))
        params['exclude_patterns'] = sorted(data.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**']))
    return params


@bp.route('/dependencies', methods=['POST'])
@measure_execution_time
@cached_endpoint('dependencies', params_extractor=dependencies_params_extractor)
def analyze_dependencies():
    """Extract and analyze dependencies from Python code."""
    if not request.json or 'path' not in request.json:
        return error_response("Missing required parameter: 'path'")
    
    repo_path = request.json['path']
    if not validate_path(repo_path):
        return error_response(f"Invalid or inaccessible path: {repo_path}")
    
    # Check if repository has been modified since last cache
    if check_repo_modified(repo_path):
        # If repository was modified, invalidate all related caches
        repo_key = get_repo_cache_key(repo_path)
        invalidate_cache('dependencies', repo_key)
    
    try:
        # Get optional parameters
        include_patterns = request.json.get('include_patterns', ['**/*.py'])
        exclude_patterns = request.json.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**'])
        output_dir = request.json.get('output_dir', os.path.join(os.getcwd(), 'output'))
        output_file = request.json.get('output_file', 'python_dependencies.json')
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize extractor
        extractor = PythonDependencyExtractor(
            repo_path, 
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        # Extract dependencies
        dependencies = extractor.extract_dependencies()
        
        # Generate output
        output_path = os.path.join(output_dir, output_file)
        extractor.to_json(output_path)
        
        # Prepare response
        response_data = {
            'success': True,
            'repo_path': repo_path,
            'module_count': len(dependencies.keys()),
            'dependency_count': sum(len(deps) for deps in dependencies.values()),
            'output_path': os.path.abspath(output_path),
            'execution_time': g.execution_times.get('analyze_dependencies', 0)
        }
        
        # Update repository modified time after successful analysis
        update_repo_modified_time(repo_path)
            
        return json_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in dependency analysis: {str(e)}", exc_info=True)
        return error_response(f"Analysis failed: {str(e)}", 500)


def metrics_params_extractor(request, *args, **kwargs):
    """Extract cache key parameters for metrics analysis."""
    params = {}
    if request.is_json:
        data = request.get_json()
        params['path'] = data.get('path')
        params['include_patterns'] = sorted(data.get('include_patterns', ['**/*']))
        params['exclude_patterns'] = sorted(data.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**']))
    return params


@bp.route('/metrics', methods=['POST'])
@measure_execution_time
@cached_endpoint('metrics', params_extractor=metrics_params_extractor)
def analyze_metrics():
    """Collect code metrics from a repository."""
    if not request.json or 'path' not in request.json:
        return error_response("Missing required parameter: 'path'")
    
    repo_path = request.json['path']
    if not validate_path(repo_path):
        return error_response(f"Invalid or inaccessible path: {repo_path}")
    
    # Check if repository has been modified since last cache
    if check_repo_modified(repo_path):
        # If repository was modified, invalidate all related caches
        repo_key = get_repo_cache_key(repo_path)
        invalidate_cache('metrics', repo_key)
    
    try:
        # Get optional parameters
        include_patterns = request.json.get('include_patterns', ['**/*'])
        exclude_patterns = request.json.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**'])
        output_dir = request.json.get('output_dir', os.path.join(os.getcwd(), 'output'))
        output_file = request.json.get('output_file', 'metrics.json')
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize metrics collector
        collector = MetricsCollector(
            repo_path, 
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        # Collect metrics
        collector.collect_metrics()
        
        # Generate output
        output_path = os.path.join(output_dir, output_file)
        collector.to_json(output_path)
        
        # Get summary of metrics
        language_stats = collector.get_language_statistics()
        
        # Prepare response
        response_data = {
            'success': True,
            'repo_path': repo_path,
            'total_files': collector.get_total_files(),
            'total_lines': collector.get_total_lines(),
            'language_stats': language_stats,
            'output_path': os.path.abspath(output_path),
            'execution_time': g.execution_times.get('analyze_metrics', 0)
        }
        
        # Update repository modified time after successful analysis
        update_repo_modified_time(repo_path)
            
        return json_response(response_data)
        
    except Exception as e:
        logger.error(f"Error in metrics analysis: {str(e)}", exc_info=True)
        return error_response(f"Analysis failed: {str(e)}", 500)


# For the full analysis, we don't cache the endpoint itself since it's
# a longer running operation that is tracked with a job ID. Instead,
# we'll cache individual steps of the analysis
@bp.route('/full', methods=['POST'])
@measure_execution_time
def analyze_full():
    """Run a complete analysis pipeline on a repository."""
    if not request.json or 'path' not in request.json:
        return error_response("Missing required parameter: 'path'")
    
    repo_path = request.json['path']
    if not validate_path(repo_path):
        return error_response(f"Invalid or inaccessible path: {repo_path}")
    
    try:
        # Get optional parameters
        include_patterns = request.json.get('include_patterns', ['**/*'])
        exclude_patterns = request.json.get('exclude_patterns', ['**/venv/**', '**/.git/**', '**/__pycache__/**'])
        output_dir = request.json.get('output_dir', os.path.join(os.getcwd(), 'output'))
        create_bundle = request.json.get('create_bundle', False)
        
        # Generate a unique job ID
        job_id = generate_unique_id()
        
        # Create job status
        analysis_jobs[job_id] = {
            'job_id': job_id,
            'status': 'started',
            'repo_path': repo_path,
            'output_dir': output_dir,
            'created_at': g.execution_times.get('start_time', 0),
            'steps': {
                'file_tree': 'pending',
                'dependencies': 'pending',
                'metrics': 'pending',
                'visualization': 'pending',
                'summary': 'pending',
                'bundle': 'pending' if create_bundle else 'skipped'
            }
        }
        
        # Check if repository has been modified since last cache
        if check_repo_modified(repo_path):
            # If repository was modified, invalidate all related caches
            repo_key = get_repo_cache_key(repo_path)
            # Invalidate caches for all analysis types
            for analysis_type in ['file_tree', 'dependencies', 'metrics', 'visualization', 'summary']:
                invalidate_cache(analysis_type, repo_key)
        
        # This would typically be done asynchronously in a real application
        # Here we'll just update the status as we go
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize data collector
        collector = DataCollector(repo_path, output_dir)
        
        # Update job status
        analysis_jobs[job_id]['status'] = 'processing'
        
        # Step 1: File Tree
        analysis_jobs[job_id]['steps']['file_tree'] = 'processing'
        file_tree = collector.collect_file_tree()
        analysis_jobs[job_id]['steps']['file_tree'] = 'completed'
        
        # Step 2: Dependencies
        analysis_jobs[job_id]['steps']['dependencies'] = 'processing'
        dependencies = collector.collect_python_dependencies()
        analysis_jobs[job_id]['steps']['dependencies'] = 'completed'
        
        # Step 3: Metrics
        analysis_jobs[job_id]['steps']['metrics'] = 'processing'
        metrics = collector.collect_metrics()
        analysis_jobs[job_id]['steps']['metrics'] = 'completed'
        
        # Step 4: Visualization
        analysis_jobs[job_id]['steps']['visualization'] = 'processing'
        visualizations = collector.generate_visualizations()
        analysis_jobs[job_id]['steps']['visualization'] = 'completed'
        
        # Step 5: Summary
        analysis_jobs[job_id]['steps']['summary'] = 'processing'
        summary = collector.generate_summary()
        analysis_jobs[job_id]['steps']['summary'] = 'completed'
        
        # Step 6: Bundle (if requested)
        if create_bundle:
            analysis_jobs[job_id]['steps']['bundle'] = 'processing'
            
            # Create bundle configuration
            config = BundleConfig(
                bundle_dir="repo_meta",
                include_file_tree=True,
                include_dependencies=True,
                include_metrics=True,
                include_visualizations=True,
                include_summaries=True,
                cleanup_temp_files=True,
                compress_bundle=True,
                compression_format="zip"
            )
            
            # Create bundle assembler
            bundler = ContextBundleAssembler(
                repo_path=repo_path,
                output_dir=output_dir,
                config=config
            )
            
            # Generate bundle
            artifacts = bundler.collect_artifacts()
            manifest_path = bundler.generate_manifest()
            prompt_path = bundler.generate_prompt_template()
            archive_path = bundler.compress_bundle()
            
            analysis_jobs[job_id]['steps']['bundle'] = 'completed'
            analysis_jobs[job_id]['bundle_path'] = archive_path
        
        # Update job status
        analysis_jobs[job_id]['status'] = 'completed'
        analysis_jobs[job_id]['completed_at'] = g.execution_times.get('end_time', 0)
        analysis_jobs[job_id]['execution_time'] = g.execution_times.get('analyze_full', 0)
        
        # Prepare response
        response_data = {
            'success': True,
            'job_id': job_id,
            'repo_path': repo_path,
            'output_dir': output_dir,
            'status': 'completed',
            'steps': analysis_jobs[job_id]['steps'],
            'execution_time': g.execution_times.get('analyze_full', 0)
        }
            
        return json_response(response_data)
        
    except Exception as e:
        # Update job status on error
        if 'job_id' in locals():
            analysis_jobs[job_id]['status'] = 'failed'
            analysis_jobs[job_id]['error'] = str(e)
            
        logger.error(f"Error in full analysis: {str(e)}", exc_info=True)
        return error_response(f"Analysis failed: {str(e)}", 500) 