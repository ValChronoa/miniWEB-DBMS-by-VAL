from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    from .models import StorageManager
    storage = StorageManager(app.config['DATABASE_PATH'])
    storage.init_lab_schemas()
    
    # Register blueprints/routes
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app