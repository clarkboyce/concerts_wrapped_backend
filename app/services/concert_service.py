
from rapidfuzz import fuzz, process
from app.models.concert import Concert
from app.schemas.concert import ConcertSchema
from app.extensions import db
from app.services.user_concerts_service import add_user_concert
 # Changed from user_concerts to concert
from app.extensions import db

CONFIDENCE_THRESHOLD = 60  # Adjust as neededx

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

# def delete_concert(id):
#     concert = Concert.query.get(id)
#     if not concert:
#         abort(404, "Concert not found")

#     db.session.delete(concert)
#     db.session.commit()
#     return {"message": "Concert deleted successfully"}

def process_concert_tickets(tickets, user_id=None):
    results = []

    for ticket in tickets:
        artist = ticket.get("artist")
        date = ticket.get("date")
        city = ticket.get("city")
        ticket_price = ticket.get("ticket_price")

        if not (artist and date and city):
            results.append({"ticket": ticket, "error": "Missing required fields"})
            continue

        # Fuzzy match against existing concerts
        concerts = Concert.query.filter_by(date=date, city=city).all()
        concert_names = [concert.artist for concert in concerts]

        match = process.extractOne(
            artist, concert_names, scorer=fuzz.ratio
        )  # Extract the best match and its confidence

        if match and match[1] >= CONFIDENCE_THRESHOLD:
            # Match found
            matched_concert = next(
                (c for c in concerts if c.artist == match[0]), None
            )
            if matched_concert:
                if user_id:
                    # Add the user to the concert
                    add_user_concert(user_id, matched_concert.id, ticket_price, date)
                results.append(
                    {
                        "ticket": ticket,
                        "status": "Matched",
                        "concert": ConcertSchema().dump(matched_concert),
                    }
                )
                continue

        # No match found: Create a new concert
        new_concert = Concert(
            artist=artist,
            date=date,
            city=city,
            state="Unknown",  # Hardcoded value
            venue="Unknown Venue",  # Hardcoded value
            genres="Unknown",  # Hardcoded value
            capacity=0,  # Hardcoded value
            number_of_songs=0,  # Hardcoded value
        )
        db.session.add(new_concert)
        db.session.commit()

        if user_id:
            # Add the user to the new concert
            add_user_concert(user_id, new_concert.id, ticket_price, date)

        results.append(
            {
                "ticket": ticket,
                "status": "Created",
                "concert": ConcertSchema().dump(new_concert),
            }
        )

    return results