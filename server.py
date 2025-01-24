from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import pandas as pd
from thefuzz import fuzz, process
import re
import json
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_reference_data():
    """Load reference concert data from local CSV file"""
    try:
        df = pd.read_csv('concert_reference_data.csv')
        return df.to_dict('records')
    except FileNotFoundError:
        logging.error("CSV file not found. Please ensure 'concert_reference_data.csv' is in the correct directory.")
        return []

def normalize_text(text):
    """Normalize text by removing special characters and converting to lowercase"""
    if not text:
        return ""
    text = re.sub(r'[^\w\s]', '', text.lower())
    return ' '.join(text.split())

def find_best_match(query, choices, threshold=80):
    """Find the best matching string from choices using fuzzy matching"""
    if not query or not choices:
        return None
    
    normalized_query = normalize_text(query)
    normalized_choices = {normalize_text(choice): choice for choice in choices}
    
    best_match = process.extractOne(
        normalized_query,
        normalized_choices.keys(),
        scorer=fuzz.token_set_ratio
    )
    
    if best_match and best_match[1] >= threshold:
        matched = normalized_choices[best_match[0]]
        logging.info(f"Matched '{query}' to '{matched}' with confidence {best_match[1]}")
        return matched
    logging.info(f"No suitable match found for '{query}'")
    return None

def get_additional_info_from_api(artist_name, city, date):
    """Fetch additional info from Perplexity API"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Payload for capacity and price
    payload = {
        'model': 'sonar',
        'messages': [
            {'role': 'system', 'content': 'Provide accurate information about the concert.'},
            {'role': 'user', 'content': f'What is the venue capacity and average ticket price for {artist_name} performing in {city} on {date}?'}
        ],
        'response_format': {
            'type': 'json',
            'json': {
                'venue_capacity': 'integer|null',
                'average_ticket_price': 'number|null',
                'genres': 'array|null'
            }
        }
    }
    
    try:
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            data = json.loads(content)
            logging.info(f"Retrieved API data: {data}")
            return data
        else:
            logging.error(f"API Error: {response.status_code}")
            return None
            
    except Exception as e:
        logging.error(f"Error calling Perplexity API: {e}")
        return None

def get_artist_info(artist_name, city, date, reference_data):
    """Look up artist info from reference data with fuzzy matching"""
    if not reference_data:
        logging.error("No reference data available")
        return None

    logging.info(f"Searching for - Artist: {artist_name}, City: {city}, Date: {date}")

    all_artists = list(set(concert['Artist'] for concert in reference_data))
    all_cities = list(set(concert['City'] for concert in reference_data))
    
    matched_artist = find_best_match(artist_name, all_artists)
    matched_city = find_best_match(city, all_cities)
    
    # Input date is already in DD-MM-YYYY format, no need to convert
    logging.info(f"Matched artist: {matched_artist}")
    logging.info(f"Matched city: {matched_city}")
    logging.info(f"Input date: {date}")
    
    # Try to find exact match using all three fields
    if matched_artist and matched_city and date:
        for concert in reference_data:
            logging.info(f"Comparing with concert: {concert}")
            
            concert_date = concert.get('Date')
            if (concert['Artist'].lower() == matched_artist.lower() and 
                concert['City'].lower() == matched_city.lower() and 
                concert_date == date):
                
                logging.info(f"Found exact match for {matched_artist} in {matched_city} on {date}")
                return {
                    'genres': concert.get('Genres', '').split(',') if concert.get('Genres') else [],
                    'venue_capacity': concert.get('Capacity'),
                    'average_ticket_price': concert.get('Price'),
                    'venue_name': concert.get('Venue'),
                    'state': concert.get('State'),
                    'matched_artist': matched_artist,
                    'matched_city': matched_city,
                    'source': 'reference_exact_match'
                }
    
    # Try to find match with just artist and date
    if matched_artist and date:
        for concert in reference_data:
            concert_date = concert.get('Date')
            if (concert['Artist'].lower() == matched_artist.lower() and 
                concert_date == date):
                
                logging.info(f"Found partial match (artist and date) for {matched_artist} on {date}")
                return {
                    'genres': concert.get('Genres', '').split(',') if concert.get('Genres') else [],
                    'venue_capacity': concert.get('Capacity'),
                    'average_ticket_price': concert.get('Price'),
                    'venue_name': concert.get('Venue'),
                    'state': concert.get('State'),
                    'matched_artist': matched_artist,
                    'matched_city': concert['City'],
                    'source': 'reference_partial_match'
                }
    
    logging.info(f"No reference data match found, trying Perplexity API for {artist_name}")
    api_data = get_additional_info_from_api(artist_name, city, date)
    if api_data:
        api_data.update({
            'matched_artist': matched_artist or artist_name,
            'matched_city': matched_city or city,
            'source': 'perplexity_api'
        })
    return api_data

if __name__ == '__main__':
    app.run(port=5000, debug=True) 