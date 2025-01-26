from app.models.user_concerts import UsersConcert  # Ensure you have the correct import here
from app.schemas.user_concerts import UsersConcertSchema

from app.extensions import db
from flask import abort
from datetime import datetime

def add_user_concert(user_id, concert_id, ticket_price, concert_date):
    if not user_id or not concert_id or not concert_date:
        abort(400, "userId, concertId, and concertDate are required")

    try:
        # Parse the concert_date from string to date (YYYY-MM-DD format)
        concert_date = datetime.strptime(concert_date, "%Y-%m-%d").date()
    except ValueError:
        abort(400, "Invalid date format. Use YYYY-MM-DD")
    
    # Check if the user already has a concert entry with the same user_id and concert_id
    existing_concert = UsersConcert.query.filter_by(user_id=user_id, concert_id=concert_id).first()
    
    if existing_concert:
        abort(400, "This user is already attending this concert")
    
    # Create a new UsersConcert entry if no duplicates are found
    user_concert = UsersConcert(user_id=user_id, concert_id=concert_id, 
                                user_ticket_price=ticket_price, timestamp=concert_date)
    db.session.add(user_concert)
    db.session.commit()

    return UsersConcertSchema().dump(user_concert), 201

def get_all_user_concerts(user_id):
    if not user_id:
        abort(400, "userId is required")

    # Query all concerts for a specific user
    user_concerts = UsersConcert.query.filter_by(user_id=user_id).all()
    
    # Return all user concerts using schema
    return UsersConcertSchema(many=True).dump(user_concerts)

def update_user_concert(id, concert_id, ticket_price):
    user_concert = UsersConcert.query.get(id)
    if not user_concert:
        abort(404, "User concert not found")

    user_concert.concert_id = concert_id
    if ticket_price is not None:
        user_concert.user_ticket_price = ticket_price

    db.session.commit()
    return UsersConcertSchema().dump(user_concert)

def delete_user_concert(user_id, concert_id):
    # Query to find the user concert entry based on user_id and concert_id
    user_concert = UsersConcert.query.filter_by(user_id=user_id, concert_id=concert_id).first()
    
    if not user_concert:
        abort(404, "User concert not found")

    db.session.delete(user_concert)
    db.session.commit()
    return {"message": "User concert deleted successfully"}