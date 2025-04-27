from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "site.db"

def create_app():
    """
    Factory function that creates and configures the Flask application
    
    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')
    
    db.init_app(app)
    
    from .routes.auth import auth
    from .routes.posts import posts
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(posts, url_prefix='/posts')
    
    from .models import user, post
    
    create_database(app)
    
    return app

def create_database(app):
    """
    Creates the database if it doesn't exist
    
    Args:
        app (Flask): The Flask application
    """
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!') 