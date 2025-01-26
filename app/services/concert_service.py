from app.models.concert import Concert
from app.schemas.concert import ConcertSchema  # Changed from user_concerts to concert
from app.models.user_concerts import UsersConcert  # Added import
from app.extensions import db
from flask import abort

def get_concerts(artist=None, city=None, state=None, date=None):
    query = Concert.query
    if artist:
        query = query.filter(Concert.artist.ilike(f"%{artist}%"))
    if city:
        query = query.filter(Concert.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Concert.state.ilike(f"%{state}%"))
    if date:
        query = query.filter(Concert.date == date)

    concerts = query.all()
    return ConcertSchema(many=True).dump(concerts)  # Changed schema name

def delete_concert(id):
    concert = Concert.query.get(id)
    if not concert:
        abort(404, "Concert not found")

    db.session.delete(concert)
    db.session.commit()
    return {"message": "Concert deleted successfully"}

def create_concert(data, user_id=None):
    # Search for an existing concert with matching artist, date, and venue
    existing_concert = Concert.query.filter_by(
        artist=data["artist"],
        date=data["date"],
        venue=data["venue"]
    ).first()

    if existing_concert:
        # If a concert already exists, associate the user with the concert if user_id is provided
        if user_id:
            # Add the concert to the user's concert list
            from app.services.user_concerts_service import add_user_concert
            ticket_price = data.get("ticketPrice", 0)  # Example: Pass ticket price if it's part of the data
            concert_date = data["date"]
            return add_user_concert(user_id, existing_concert.id, ticket_price, concert_date)
        
        # Return the existing concert details without adding a new one
        return ConcertSchema().dump(existing_concert), 200
    
    # If no concert exists, create a new one
    concert = Concert(
        artist=data["artist"],
        genres=data["genres"],
        date=data["date"],
        venue=data["venue"],
        city=data["city"],
        state=data["state"],
        capacity=data["capacity"],
        number_of_songs=data["number_of_songs"]
    )
    db.session.add(concert)
    db.session.commit()

    # Return newly created concert details
    return ConcertSchema().dump(concert), 201