from flask import Blueprint, request, jsonify
from app.services.concert_service import process_concert_tickets, get_concerts

concert_bp = Blueprint("concert", __name__)

@concert_bp.route("/", methods=["POST"])
def process_concerts_view():
    data = request.get_json()
    user_id = data.get("userId")  # Expecting userId in the request body
    tickets = data.get("tickets", [])

    if not tickets:
        return jsonify({"error": "No tickets provided"}), 400

    results = process_concert_tickets(tickets, user_id)
    return jsonify(results), 200

@concert_bp.route("/", methods=["GET"])
def get_concerts_view():
    # Get query parameters from the request
    artist = request.args.get("artist")
    city = request.args.get("city")
    date = request.args.get("date")

    # Fetch concerts using the provided service, applying filters
    results = get_concerts(artist=artist, city=city, date=date)

    # Limit the results to 20 concerts
    limited_results = results[:20]

    # Return the limited results as JSON
    return jsonify(limited_results), 200


#  [
#   {
#     "concert": {
#       "id": 1,
#       "artist": "Artist Name",
#       "date": "2024-03-20",
#       "city": "City Name",
#       "state": "State",
#       "venue": "Venue Name",
#       "genres": "Rock",
#       "capacity": 1000,
#       "number_of_songs": 20
#     },
#     "ticket_price": 99.99
#   },
#   // ... more concerts
# ]