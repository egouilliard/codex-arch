"""
API documentation module for Codex-Arch.

This module provides the functionality to generate OpenAPI/Swagger
documentation for the Codex-Arch REST API.
"""

import os
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Blueprint, jsonify, current_app, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

from codex_arch import __version__
from codex_arch.api.routes import info, analysis, artifacts, auth

# Create blueprint for API documentation
bp = Blueprint('docs', __name__)

# Define API metadata
OPENAPI_TITLE = "Codex-Arch API"
OPENAPI_VERSION = __version__
OPENAPI_DESCRIPTION = "API for Codex Architecture Analysis Tool"

def register_swagger_docs(app):
    """
    Register Swagger UI blueprint with the Flask app.
    
    Args:
        app: Flask application instance
    """
    api_version = app.config.get('API_VERSION', 'v1')
    
    # URL for accessing OpenAPI specification
    swagger_url = f'/api/{api_version}/docs'
    
    # URL for accessing OpenAPI JSON
    api_url = f'/api/{api_version}/swagger.json'
    
    # Register Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            'app_name': OPENAPI_TITLE,
            'dom_id': '#swagger-ui',
            'layout': 'BaseLayout',
            'deepLinking': True,
            'showExtensions': True,
            'showCommonExtensions': True
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
    app.register_blueprint(bp, url_prefix=f'/api/{api_version}')

def create_apispec():
    """
    Create and configure the APISpec object.
    
    Returns:
        APISpec object with all documented endpoints
    """
    # Create spec
    spec = APISpec(
        title=OPENAPI_TITLE,
        version=OPENAPI_VERSION,
        openapi_version="3.0.2",
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
        info={
            'description': OPENAPI_DESCRIPTION,
            'contact': {'email': 'support@codex-arch.example.com'},
            'license': {'name': 'MIT', 'url': 'https://opensource.org/licenses/MIT'},
        },
    )
    
    # Add servers configuration
    spec.servers = [
        {"url": "{protocol}://{hostname}/api/v1", "description": "API server", 
         "variables": {
             "protocol": {"enum": ["http", "https"], "default": "https"},
             "hostname": {"default": "api.codex-arch.example.com"}
         }}
    ]
    
    # Add security schemes
    spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    
    # Register paths from all route blueprints
    register_routes(spec, info.bp)
    register_routes(spec, analysis.bp)
    register_routes(spec, artifacts.bp)
    register_routes(spec, auth.bp)
    
    return spec

def register_routes(spec, blueprint):
    """
    Register routes from a blueprint in the API spec.
    
    Args:
        spec: APISpec object
        blueprint: Flask Blueprint object
    """
    # For each endpoint in the blueprint
    for endpoint, view_func in blueprint.view_functions.items():
        # Extract documentation from docstring
        if view_func.__doc__:
            spec.path(view=view_func, path=get_path_from_endpoint(blueprint, endpoint))

def get_path_from_endpoint(blueprint, endpoint):
    """
    Get the URL path from an endpoint.
    
    Args:
        blueprint: Flask Blueprint
        endpoint: Endpoint name
        
    Returns:
        URL path for the endpoint
    """
    endpoint_name = endpoint.replace(f"{blueprint.name}.", "")
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == endpoint:
            return rule.rule
    return f"/{blueprint.url_prefix}/{endpoint_name}"

@bp.route('/swagger.json')
def get_swagger_json():
    """
    Endpoint to serve the OpenAPI specification as JSON.
    
    Returns:
        JSON serialized OpenAPI specification
    """
    spec = create_apispec()
    return jsonify(spec.to_dict())

@bp.route('/postman-collection')
def get_postman_collection():
    """
    Endpoint to download the Postman collection for API testing.
    
    Returns:
        Postman collection JSON file
    """
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')
    return send_from_directory(
        docs_dir, 
        'codex-arch-api-collection.json',
        as_attachment=True,
        download_name='codex-arch-api-collection.json'
    ) 