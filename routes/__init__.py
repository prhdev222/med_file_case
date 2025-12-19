from flask import Blueprint

# Import all route modules
from .public import public_bp
from .admin import admin_bp
from .api import api_bp
from .admin_api import admin_api_bp

# List of all blueprints to register
blueprints = [
    public_bp,
    admin_bp,
    api_bp,
    admin_api_bp
]

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    for blueprint in blueprints:
        app.register_blueprint(blueprint)