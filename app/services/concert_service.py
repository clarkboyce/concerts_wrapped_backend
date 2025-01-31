from rapidfuzz import fuzz, process
from app.models.concert import Concert
from app.schemas.concert import ConcertSchema
from app.extensions import db
from app.services.user_concerts_service import add_user_concert
 # Changed from user_concerts to concert
from app.extensions import db
from app.services.perplexity import search_events  # The function above




CONFIDENCE_THRESHOLD = 60  # Adjust as neededx

def get_concerts(artist=None, city=None, date=None):
    query = Concert.query
    if artist:
        query = query.filter(Concert.artist.ilike(f"%{artist}%"))
    if city:
        query = query.filter(Concert.city.ilike(f"%{city}%"))
    if date:
        query = query.filter(Concert.date == date)

    concerts = query.all()
    return ConcertSchema(many=True).dump(concerts)

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
                # Check if capacity is missing
                if matched_concert.capacity == 0:
                    # Search for venue capacity only
                    venue_api_response = search_events(matched_concert.venue, matched_concert.city, capacity_only=True)
                    if venue_api_response and "venue_capacity" in venue_api_response:
                        matched_concert.capacity = venue_api_response["venue_capacity"]
                        db.session.commit()

                if user_id:
                    # Add the user to the concert
                    add_user_concert(user_id, matched_concert.id, ticket_price)
                results.append(
                    {
                        "ticket": ticket,
                        "status": "Matched",
                        "concert": ConcertSchema().dump(matched_concert),
                    }
                )
                continue

         # No match found: Call Perplexity API
        api_response = search_events(artist, date, city)



        
        if not api_response or "concert_details" not in api_response:
            results.append({"ticket": ticket, "error": "No match found via API"})
            continue

        # Extract concert details from API response
        concert_data = api_response["concert_details"]

             

        new_concert = Concert(
            artist=concert_data.get("artist", artist),
            date=concert_data.get("date", date),
            city=concert_data.get("city", city),
            state=concert_data.get("state", "Unknown"),
            venue=concert_data.get("venue", "Unknown Venue"),
            genres=concert_data.get("genre", "Unknown"),  
            capacity=concert_data.get("capacity") if concert_data.get("capacity") is not None else 0,
            number_of_songs=concert_data.get("number_of_songs") if concert_data.get("number_of_songs") is not None else 0,
            average_ticket_price=concert_data.get("average_ticket_price", 50.00),
        )


        db.session.add(new_concert)
        db.session.commit()

        if user_id:
            # Add the user to the new concert
            add_user_concert(user_id, new_concert.id, ticket_price)

        results.append(
            {
                "ticket": ticket,
                "status": "Created",
                "concert": ConcertSchema().dump(new_concert),
            }
        )

    return results