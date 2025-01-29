import requests
from pydantic import BaseModel
import datetime
import json

url = "https://api.perplexity.ai/chat/completions"
API_KEY = ""  # Replace with your API key

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

def search_events(artist, date, city):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI that helps find concert details. Given an artist, date, and city, "
                    "provide the state, venue, genre, capacity as exact integer value, number of songs as exact integer value, and specific average ticket price between (0-10000) as exact float value. "
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
        response = requests.post(url, headers=headers, json=payload)
        print("Raw API Response:", response.text)  # Print raw response
        response_data = response.json()
        print("Response Data:", response_data)  # Print raw response

        if "choices" in response_data and response_data["choices"]:
            content = response_data["choices"][0]["message"]["content"]

            # Remove the markdown code block and strip extra spaces
            content = content.strip('```json\n').strip('```')

            # Try to parse the content as JSON
            try:
                json_event_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON content: {e}")
                return None

            # Access the confidence score and check it
            confidence = json_event_data.get("confidence_score", 0)

            if confidence < CONFIDENCE_THRESHOLD:
                print(f"Low confidence ({confidence}%), ignoring Perplexity API result.")
                return None  # Reject result if confidence is too low

            return json_event_data  # Return the parsed dictionary
        else:
            print("No valid response from Perplexity API")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error querying Perplexity API: {e}")
        return None

def main():
    # Example inputs for testing
    artist = "Taylor Swift"
    date = "2023-08-3"
    city = "Los Angeles"

    print("Testing search_events with the following inputs:")
    print(f"Artist: {artist}, Date: {date}, City: {city}")
    
    result = search_events(artist, date, city)

    if result:
        print("\nAPI Response:")
        print(result)
    else:
        print("\nNo valid response received from the API.")

if __name__ == "__main__":
    main()