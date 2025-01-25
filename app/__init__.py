from flask import Flask
from flask_cors import CORS
from app.extensions import db
from app.config import Config

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints (for routes)
    from app.routes.concert_routes import concert_bp
    from app.routes.user_concerts_routes import user_concerts_bp
    
    app.register_blueprint(concert_bp, url_prefix='/api/concerts')
    app.register_blueprint(user_concerts_bp, url_prefix='/api/user-concerts')

    return app