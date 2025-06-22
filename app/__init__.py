from flask import Flask
from .routes import init_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize routes
    init_routes(app)
    
    return app