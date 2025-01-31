import pytest
from app.services.concert_service import process_tickets
from app.services.perplexity import search_events
from app.models import Concert, User
from datetime import datetime, date

def test_concert_matching():
    # Test data
    test_tickets = [
        {
            "artist": "Taylor Swift",
            "date": "2024-07-15",
            "city": "Los Angeles",
            "ticket_price": 500.0
        },
        {
            "artist": "The Weeknd",  # Slightly misspelled to test matching
            "date": "2024-08-20",
            "city": "New York",
            "ticket_price": 200.0
        }
    ]
    
    results = process_tickets(test_tickets)
    assert len(results) == 2
    assert results[0]["status"] in ["Matched", "Created"]

def test_venue_capacity_lookup():
    # Test venue capacity search
    result = search_events("Madison Square Garden", None, "New York", capacity_only=True)
    assert result is not None
    assert "venue_capacity" in result
    assert isinstance(result["venue_capacity"], int)
    assert result["confidence_score"] >= 70

def test_missing_capacity_update():
    # Create a concert with missing capacity
    concert = Concert(
        artist="Ed Sheeran",
        date=date(2024, 9, 1),
        city="Miami",
        venue="Kaseya Center",
        capacity=0  # Missing capacity
    )
    db.session.add(concert)
    db.session.commit()

    # Process ticket that should trigger capacity lookup
    test_ticket = {
        "artist": "Ed Sheeran",
        "date": "2024-09-01",
        "city": "Miami",
        "ticket_price": 150.0
    }
    

    result = process_tickets([test_ticket])
    updated_concert = Concert.query.filter_by(artist="Ed Sheeran").first()
    assert updated_concert.capacity > 0 


#     1. Perfect Match Cases:
#    - Exact artist, date, and city match
#    - Case-insensitive matching
#    - Slight misspellings in artist names

# 2. Venue Capacity Cases:
#    - Well-known venue (should return high confidence)
#    - Lesser-known venue (should still work but maybe lower confidence)
#    - Non-existent venue (should handle gracefully)
#    - Venue with special characters in name

# 3. Error Cases:
#    - Missing required fields
#    - Invalid date formats
#    - Empty city/venue names
#    - API timeout scenarios
#    - Rate limit handling

# 4. Edge Cases:
#    - Very long venue names
#    - International venues
#    - Multiple venues with similar names
#    - Venues that have changed names recently