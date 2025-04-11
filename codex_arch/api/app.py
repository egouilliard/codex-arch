"""
Main Flask application for the Codex-Arch REST API.
"""

import os
import logging
import datetime
from typing import Optional, Dict, Any
from flask import Flask, jsonify, g, request, render_template
from flask_cors import CORS
from flask_caching import Cache

from codex_arch.api.config import get_config
from codex_arch import __version__

logger = logging.getLogger(__name__)
cache = Cache()

def create_app(testing: bool = False) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        testing: Whether to use testing configuration
        
    Returns:
        Configured Flask application
    """
    # Create the Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Override with testing config if requested
    if testing:
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize cache
    cache.init_app(app)
    
    # Register before_request handler for cache tracking
    @app.before_request
    def before_request():
        from codex_arch.api.cache.stats import init_request_cache_tracking
        
        # Initialize cache tracking
        init_request_cache_tracking()
        
        # Start measuring execution time
        from codex_arch.api.utils import start_execution_timer
        start_execution_timer()
    
    # Register after_request handler for cache tracking
    @app.after_request
    def after_request(response):
        from codex_arch.api.cache.stats import track_cache_hit
        
        # Track cache hit
        track_cache_hit()
        
        return response
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
        
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
        
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    # Register API routes
    from codex_arch.api.routes import info
    from codex_arch.api.routes import analysis
    from codex_arch.api.routes import artifacts
    from codex_arch.api.routes import auth
    
    # Basic info route
    @app.route('/')
    def index():
        """
        Landing page for the API with links to documentation and resources.
        
        Returns:
            Rendered HTML template with API information
        """
        api_version = app.config['API_VERSION']
        current_year = datetime.datetime.now().year
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return render_template(
            'index.html',
            version=__version__,
            api_version=api_version,
            current_year=current_year,
            updated_at=updated_at,
            base_url=f"/api/{api_version}"
        )
    
    # Register blueprints
    api_version = app.config['API_VERSION']
    app.register_blueprint(info.bp, url_prefix=f'/api/{api_version}/info')
    app.register_blueprint(analysis.bp, url_prefix=f'/api/{api_version}/analysis')
    app.register_blueprint(artifacts.bp, url_prefix=f'/api/{api_version}/artifacts')
    app.register_blueprint(auth.bp, url_prefix=f'/api/{api_version}/auth')
    
    # Register API documentation
    from codex_arch.api.docs import register_swagger_docs
    register_swagger_docs(app)
    
    # Add a user-friendly API docs redirect
    @app.route('/docs')
    def api_docs_redirect():
        """
        Redirect to the API documentation.
        """
        return app.redirect(f'/api/{api_version}/docs')
    
    return app 