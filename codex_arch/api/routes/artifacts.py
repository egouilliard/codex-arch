"""
Artifacts routes for the Codex-Arch REST API.

These routes handle access to generated artifacts from the analysis process.
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify, current_app, abort, g, send_file
from werkzeug.utils import safe_join, secure_filename

from codex_arch.api.utils import (
    json_response, error_response, validate_path, 
    measure_execution_time, generate_unique_id
)
from codex_arch.api.cache.utils import (
    cached_endpoint, invalidate_cache
)
from codex_arch.api.auth import token_required, admin_required

# Create blueprint
bp = Blueprint('artifacts', __name__)
logger = logging.getLogger(__name__)


def get_artifacts_in_directory(directory: str) -> List[Dict[str, Any]]:
    """Get a list of all artifacts in a directory."""
    artifacts = []
    
    if not os.path.exists(directory):
        return artifacts
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)
            
            # Get file info
            file_info = {
                'name': file,
                'path': rel_path,
                'full_path': file_path,
                'size': os.path.getsize(file_path),
                'modified': os.path.getmtime(file_path),
                'type': os.path.splitext(file)[1][1:] if '.' in file else ''
            }
            
            artifacts.append(file_info)
    
    return artifacts


def list_artifacts_params_extractor(request, *args, **kwargs):
    """Extract cache key parameters for listing artifacts."""
    return {
        'output_dir': request.args.get('output_dir', current_app.config['OUTPUT_DIR']),
        'timestamp': int(time.time() / 300)  # Cache key changes every 5 minutes
    }


@bp.route('/list', methods=['GET'])
@measure_execution_time
@cached_endpoint('artifacts_list', params_extractor=list_artifacts_params_extractor, timeout=300)
def list_artifacts():
    """List all artifacts in the output directory."""
    # Get output directory
    output_dir = request.args.get('output_dir', current_app.config['OUTPUT_DIR'])
    
    if not validate_path(output_dir):
        return error_response(f"Invalid or inaccessible output directory: {output_dir}")
    
    try:
        # Get artifacts from directory
        artifacts = get_artifacts_in_directory(output_dir)
        
        # Group artifacts by type
        artifact_types = {}
        for artifact in artifacts:
            artifact_type = artifact['type'] or 'unknown'
            if artifact_type not in artifact_types:
                artifact_types[artifact_type] = []
            artifact_types[artifact_type].append(artifact)
        
        # Prepare response
        response_data = {
            'success': True,
            'output_dir': output_dir,
            'artifact_count': len(artifacts),
            'artifact_types': artifact_types,
            'execution_time': g.execution_times.get('list_artifacts', 0)
        }
        
        return json_response(response_data)
    
    except Exception as e:
        logger.error(f"Error listing artifacts: {str(e)}", exc_info=True)
        return error_response(f"Failed to list artifacts: {str(e)}", 500)


# For file downloads, we don't cache the responses, but we do add 
# cache headers to allow browser caching
@bp.route('/download/<path:artifact_path>', methods=['GET'])
@token_required
@measure_execution_time
def download_artifact(artifact_path):
    """
    Download a specific artifact.
    
    Requires authentication.
    """
    # Get output directory
    output_dir = request.args.get('output_dir', current_app.config['OUTPUT_DIR'])
    
    if not validate_path(output_dir):
        return error_response(f"Invalid or inaccessible output directory: {output_dir}")
    
    try:
        # Construct artifact path
        full_path = os.path.join(output_dir, artifact_path)
        
        # Validate path
        if not validate_path(full_path):
            return error_response(f"Invalid or inaccessible artifact path: {full_path}", 404)
        
        # Check if path is within output directory (security check)
        try:
            real_path = os.path.realpath(full_path)
            real_output_dir = os.path.realpath(output_dir)
            if not real_path.startswith(real_output_dir):
                return error_response("Access denied: path outside of output directory", 403)
        except Exception:
            return error_response("Access denied: invalid path", 403)
        
        # Get file modification time for ETag
        mod_time = int(os.path.getmtime(full_path))
        etag = f"artifact-{mod_time}"
        
        # Check If-None-Match header for caching
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match == etag:
            return '', 304  # Not Modified
        
        # Return file with caching headers
        response = send_file(
            full_path,
            as_attachment=True,
            download_name=os.path.basename(full_path)
        )
        
        # Add caching headers
        response.headers['ETag'] = etag
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        
        return response
    
    except Exception as e:
        logger.error(f"Error downloading artifact: {str(e)}", exc_info=True)
        return error_response(f"Failed to download artifact: {str(e)}", 500)


@bp.route('/bundle/<job_id>', methods=['GET'])
@token_required
@measure_execution_time
def download_bundle(job_id):
    """
    Download a generated bundle from a job.
    
    Requires authentication.
    """
    # Import the jobs dict from the analysis module
    from codex_arch.api.routes.analysis import analysis_jobs
    
    if job_id not in analysis_jobs:
        return error_response(f"Job ID {job_id} not found", 404)
    
    job = analysis_jobs[job_id]
    
    if 'bundle_path' not in job:
        return error_response(f"No bundle was created for job {job_id}", 404)
    
    bundle_path = job['bundle_path']
    
    try:
        # Validate path
        if not validate_path(bundle_path):
            return error_response(f"Bundle file not found: {bundle_path}", 404)
        
        # Get file modification time for ETag
        mod_time = int(os.path.getmtime(bundle_path))
        etag = f"bundle-{job_id}-{mod_time}"
        
        # Check If-None-Match header for caching
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match == etag:
            return '', 304  # Not Modified
        
        # Return file with caching headers
        response = send_file(
            bundle_path,
            as_attachment=True,
            download_name=os.path.basename(bundle_path)
        )
        
        # Add caching headers
        response.headers['ETag'] = etag
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        
        return response
    
    except Exception as e:
        logger.error(f"Error downloading bundle: {str(e)}", exc_info=True)
        return error_response(f"Failed to download bundle: {str(e)}", 500)


@bp.route('/admin/cleanup', methods=['POST'])
@token_required
@admin_required
@measure_execution_time
def admin_cleanup_artifacts():
    """
    Admin endpoint to clean up old artifacts.
    
    Requires admin authentication.
    
    Request body:
        max_age_days: Maximum age of artifacts to keep (in days)
        dry_run: If true, only list artifacts that would be deleted without actually deleting them
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return error_response("Missing request data", 400)
            
        max_age_days = data.get('max_age_days', 30)
        dry_run = data.get('dry_run', False)
        
        # Get output directory
        output_dir = data.get('output_dir', current_app.config['OUTPUT_DIR'])
        
        if not validate_path(output_dir):
            return error_response(f"Invalid or inaccessible output directory: {output_dir}")
        
        # Calculate cutoff time
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        # Get artifacts
        artifacts = get_artifacts_in_directory(output_dir)
        
        # Filter artifacts by age
        old_artifacts = [
            artifact for artifact in artifacts
            if artifact['modified'] < cutoff_time
        ]
        
        # Delete artifacts if not a dry run
        deleted_count = 0
        if not dry_run:
            for artifact in old_artifacts:
                try:
                    os.remove(artifact['full_path'])
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete artifact {artifact['full_path']}: {str(e)}")
            
            # Invalidate artifacts list cache after cleanup
            invalidate_cache('artifacts_list')
        
        # Prepare response
        response_data = {
            'success': True,
            'dry_run': dry_run,
            'max_age_days': max_age_days,
            'cutoff_date': datetime.fromtimestamp(cutoff_time).isoformat(),
            'total_artifacts': len(artifacts),
            'old_artifacts_count': len(old_artifacts),
            'deleted_count': deleted_count if not dry_run else 0,
            'old_artifacts': [
                {k: v for k, v in artifact.items() if k != 'full_path'}
                for artifact in old_artifacts
            ],
            'execution_time': g.execution_times.get('admin_cleanup_artifacts', 0)
        }
        
        return json_response(response_data)
        
    except Exception as e:
        logger.error(f"Error cleaning up artifacts: {str(e)}", exc_info=True)
        return error_response(f"Failed to clean up artifacts: {str(e)}", 500) 