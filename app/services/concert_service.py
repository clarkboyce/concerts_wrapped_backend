
from rapidfuzz import fuzz, process
from app.models.concert import Concert
from app.schemas.concert import ConcertSchema
from app.extensions import db
from app.services.user_concerts_service import add_user_concert
 # Changed from user_concerts to concert
from app.extensions import db
from perplexity import search_events  # The function above




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
        api_response = search_events(artist, date, city)
        if not api_response or not api_response.get("events"):
            results.append({"ticket": ticket, "error": "No match found via API"})
            continue

        # Process Perplexity API response
        events = api_response["events"]
        new_concert_data = next((event for event in events if event.get("artist") == artist), None)

        if not new_concert_data:
            results.append({"ticket": ticket, "error": "No relevant data in API response"})
            continue

        # Step 3: Create a new concert with the API data
        new_concert = Concert(
            artist=new_concert_data.get("artist", artist),
            date=new_concert_data.get("date", date),
            city=new_concert_data.get("city", city),
            state=new_concert_data.get("state", "Unknown"),  # Fallback
            venue=new_concert_data.get("venue", "Unknown Venue"),  # Fallback
            genres=new_concert_data.get("genres", "Unknown"),  # Fallback
            capacity=new_concert_data.get("capacity", 0),  # Fallback
            number_of_songs=new_concert_data.get("number_of_songs", 0),  # Fallback
            average_ticket_price=new_concert_data.get("average_ticket_price", 50.00),  # Fallback
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