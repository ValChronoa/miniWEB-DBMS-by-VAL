import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    SETTINGS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings')
    EXPORTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'exports')
    
    # Create directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)