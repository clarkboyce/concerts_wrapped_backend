import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/concerts_wrapped'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Additional configurations can be added here
    DEBUG = True
    TESTING = False