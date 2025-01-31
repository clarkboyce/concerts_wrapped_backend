from app.extensions import db

class Concert(db.Model):
    __tablename__ = "concerts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist = db.Column(db.String(255), nullable=False)
    genres = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    number_of_songs = db.Column(db.Integer, nullable=False)
    average_ticket_price = db.Column(db.Double, nullable=True)

    # Relationship to UsersConcert
    users = db.relationship("UsersConcert", back_populates="concert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Concert {self.artist} at {self.venue}>"