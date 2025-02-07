import requests
from pydantic import BaseModel
import datetime
from typing import Optional
import json
import os
from app.utils import logger  # Import the logger


url = "https://api.perplexity.ai/chat/completions"
API_KEY =  os.getenv("PERPLEXITY_API_KEY") # Replace with your API key

CONFIDENCE_THRESHOLD = 60  # Adjust as needed

class AnswerFormat(BaseModel):
    artist: str
    date: datetime.date
    city: str
    state: str
    venue: str
    genre: str
    capacity: int
    number_of_songs: int
    confidence_score: int

class VenueCapacityFormat(BaseModel):
    venue_capacity: int
    confidence_score: int

def search_event(city, artist, date):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise. Return only factual information with high confidence.",
            },
            {
                "role": "user",
                "content": (
                    f"Find concert details for {artist} performing on {date} in {city}. "
                    "Return a JSON object with the following fields: "
                    "artist, date (YYYY-MM-DD), city, state (2-letter code), venue, one genre, "
                    "capacity (as integer), number_of_songs (as integer), and confidence_score (1-100)."
                    "Include nothing else in your response."
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": AnswerFormat.model_json_schema()},
        },
    }

    return _make_api_request(payload, headers, capacity_only=False)

def search_venue_capacity(city, venue):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise. Return only factual information with high confidence.",
            },
            {
                "role": "user",
                "content": (
                    f"What is the capacity of {venue} in {city}? "
                    "Return a JSON object with venue_capacity (as integer) "
                    "and confidence_score (1-100)."
                    "Include nothing else in your response."

                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": VenueCapacityFormat.model_json_schema()},
        },
    }

    return _make_api_request(payload, headers, capacity_only=True)

def _make_api_request(payload, headers, capacity_only):
    try:
        logger.info(
            "Querying Perplexity API for %s", 
            "venue capacity" if capacity_only else "concert details"
        )
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() 
        response_data = response.json()
        logger.debug("Raw API Response: %s", response_data)

        if "choices" in response_data and response_data["choices"]:
            content = response_data["choices"][0]["message"]["content"]
            
            try:
                logger.info("Content length: %d", len(content))
                logger.info("Content exact value: '%s'", content)
                
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                logger.info("Content after filtering: %s", content)

                json_event_data = json.loads(content)
                if json_event_data.get("venue_capacity") is None:
                        json_event_data["venue_capacity"] = 2500
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
