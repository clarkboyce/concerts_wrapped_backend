from flask import Flask
from flask_cors import CORS
from .extensions import db
from .config import Config
from .routes.concert_routes import concert_bp
from .routes.user_concerts_routes import user_concerts_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize extensions
    with app.app_context():
        db.init_app(app)
        db.create_all() # Ensure tables are created when app starts


    # Register blueprints
    app.register_blueprint(concert_bp, url_prefix='/api/concerts')
    app.register_blueprint(user_concerts_bp, url_prefix='/api/user-concerts')

    return app