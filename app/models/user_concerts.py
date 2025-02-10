from app.extensions import db

class UsersConcert(db.Model):
    __tablename__ = "user_concert"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey("concerts.id"), nullable=False)
    user_ticket_price = db.Column(db.Float, nullable=True)  # Added ticket price field
    timestamp = db.Column(db.Date, nullable=False)
    


    # Relationship to Concert
    concert = db.relationship("Concert", back_populates="users")

    def __repr__(self):
        return f"<UsersConcert User {self.user_id} attended Concert {self.concert_id}>"