import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    EXPORTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'exports')
    
    # Create directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # Database file path
    DATABASE_PATH = os.path.join(DATA_DIR, 'database.json')