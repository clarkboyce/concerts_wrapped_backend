from rapidfuzz import fuzz, process
from app.models.concert import Concert
from app.schemas.concert import ConcertSchema
from app.extensions import db
from app.services.user_concerts_service import add_user_concert
 # Changed from user_concerts to concert
from app.extensions import db
from app.services.perplexity import search_event  # The function above
from app.services.perplexity import search_venue_capacity
from sqlalchemy import inspect




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
    # Debug: Print model inspection
    inspector = inspect(Concert)
    print("Model attributes:", [c.key for c in inspector.attrs])
    print("Model columns:", [c.name for c in inspector.columns])
    
    results = []

    for ticket in tickets:
        artist = ticket.get("artist")
        date = ticket.get("date")
        city = ticket.get("city")
        ticket_price = ticket.get("ticket_price")

        try:
            # Debug the query before execution
            query = Concert.query.filter_by(date=date, city=city)
            print("SQL Query:", str(query))
            
            concerts = query.all()
            print(f"Found {len(concerts)} concerts")
            
        except Exception as e:
            print(f"Query error: {str(e)}")
            raise

        if not (artist and date and city):
            results.append({"ticket": ticket, "error": "Missing required fields"})
            continue

        # Fuzzy match against existing concerts
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
                    venue_api_response = search_venue_capacity(matched_concert.city, matched_concert.venue)
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
        api_response = search_event(city, artist, date)
        
        if not api_response:
            print(f"Perplexity API returned no response for {artist} in {city} on {date}")
            results.append({"ticket": ticket, "error": "Perplexity API call failed"})
            continue
            
        concert_data = api_response  # Direct access, no more .get("concert_details", {})
        missing_fields = []
        
        # Check required fields
        if not concert_data.get("artist"):
            missing_fields.append("artist")
        if not concert_data.get('venue'):
            missing_fields.append("venue")
        if not concert_data.get("city"):
            missing_fields.append("city")
        if not concert_data.get("state"):
            missing_fields.append("state")
            
        # Capacity might be 0 or missing, that's okay
        if concert_data.get("capacity") is None:
            print(f"No capacity data for venue {concert_data.get('venue', 'unknown')}")
        
        if missing_fields:
            print(f"Perplexity API response missing fields: {', '.join(missing_fields)}")
            print(f"Raw API response: {api_response}")
            results.append({
                "ticket": ticket, 
                "error": f"Incomplete data from API. Missing: {', '.join(missing_fields)}"
            })
            continue

        new_concert = Concert(
            artist=concert_data.get("artist", artist),
            date=concert_data.get("date", date),
            city=concert_data.get("city", city),
            state=concert_data.get("state", "Unknown"),
            venue=concert_data.get("venue", "Unknown Venue"),
            genres=concert_data.get("genre", "Unknown"),  
            capacity=concert_data.get("capacity") if concert_data.get("capacity") is not None else 0,
            number_of_songs=concert_data.get("number_of_songs") if concert_data.get("number_of_songs") is not None else 0,
        )


        db.session.add(new_concert)
        db.session.commit()

        if user_id:
            # Add the user to the new concert with their specific ticket price
            add_user_concert(user_id, new_concert.id, ticket_price)

        results.append(
            {
                "ticket": ticket,
                "status": "Created",
                "concert": ConcertSchema().dump(new_concert),
            }
        )

    return results