from flask import Flask
from app.config import Config  # Or from .config import Config
from app.routes import routes  # Or from .routes import routes

def create_app():
    """
    Initialize the Flask application and load the configuration.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(routes)
    return app