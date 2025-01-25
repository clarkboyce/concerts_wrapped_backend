from app.models.concert import Concert
from app.schemas.concert import ConcertSchema  # Changed from user_concerts to concert
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

def create_concert(data):
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
    return ConcertSchema().dump(concert), 201  # Changed schema name