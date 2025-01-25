from app import create_app
from app.extensions import db
from app.models.concert import Concert
from app.models.user_concerts import UserConcert  # Updated to match file name

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()