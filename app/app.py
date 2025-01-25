from flask import Flask
from app.extensions import db
from app.routes.concert_routes import concert_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(concert_bp, url_prefix="/api/concerts")

    return app