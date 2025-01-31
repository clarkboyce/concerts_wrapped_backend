import requests
from pydantic import BaseModel
import datetime
import json
import os
from app.utils import logger  # Import the logger


url = "https://api.perplexity.ai/chat/completions"
API_KEY =  os.getenv("PERPLEXITY_API_KEY") # Replace with your API key

CONFIDENCE_THRESHOLD = 70  # Adjust as needed

class AnswerFormat(BaseModel):
    artist: str
    date: datetime.date
    city: str
    state: str
    venue: str
    genre: str
    capacity: int
    number_of_songs: int
    average_ticket_price: float
    confidence_score: int

class VenueCapacityFormat(BaseModel):
    venue_capacity: int
    confidence_score: int

def search_events(artist, date, city, capacity_only=False):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    if capacity_only:
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an AI that helps find venue capacity. Given venue name and city, return capacity as integer in JSON with confidence_score (1-100). "
                        "Format: {\"venue_capacity\": int, \"confidence_score\": int}"
                    ),
                },
                {
                    "role": "user",
                    "content": f"What is the capacity of {artist} venue in {city}?",  # artist parameter is used as venue name
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": VenueCapacityFormat.model_json_schema()},
            },
        }
    else:
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an AI that helps find concert details. Given an artist, date, and city, "
                        "provide the state, venue, genre, capacity as exact integer value, and specific average ticket price between (0-10000) as exact float value. "
                        "Your response must be in JSON format DO NOT WRITE NORMAL TEXT and include a confidence_score (1-100)."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Find concert details for {artist} performing on {date} in {city}.",
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": AnswerFormat.model_json_schema()},
            },
        }

    try:
        logger.info(
            "Querying Perplexity API for %s: %s, city: %s", 
            "venue capacity" if capacity_only else "artist",
            artist,
            city
        )
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() 
        response_data = response.json()
        logger.debug("Raw API Response: %s", response_data)

        if "choices" in response_data and response_data["choices"]:
            content = response_data["choices"][0]["message"]["content"].strip('```json\n').strip('```')

            try:
                json_event_data = json.loads(content)
                if not capacity_only:
                    json_event_data["number_of_songs"] = 12
                logger.info("Parsed JSON from API: %s", json_event_data)
            except json.JSONDecodeError as e:
                logger.error("Error parsing JSON content: %s", e, exc_info=True)
                return None

            confidence = json_event_data.get("confidence_score") or json_event_data.get("concert_details", {}).get("confidence_score", 0)
            
            if confidence < CONFIDENCE_THRESHOLD:
                logger.warning("Low confidence (%d%%), ignoring API result.", confidence)
                return None  

            return json_event_data  

        else:
            logger.error("No valid response from Perplexity API")
            return None

    except requests.exceptions.RequestException as e:
        logger.error("Error querying Perplexity API: %s", e, exc_info=True)
        return None
