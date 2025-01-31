from datetime import datetime
import csv
from app import create_app, db
from app.models import Concert

def load_concert_data():
    app = create_app()
    
    with app.app_context():
        # First, let's clear existing data (optional)
        Concert.query.delete()
        db.session.commit()
        
        # Read and process the CSV file
        with open('app/concert_reference_data.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Convert date string to datetime object
                date_obj = datetime.strptime(row['Date'], '%d-%m-%Y').date()
                
                # Create new concert entry
                concert = Concert(
                    artist=row['Artist'],
                    genres=row['Genres'],
                    date=date_obj,
                    venue=row['Venue'],
                    city=row['City'],
                    state=row['State'],
                    capacity=int(row['Capacity']) if row['Capacity'] != 'null' else None,
                    number_of_songs=int(row['Number of Songs']),
                    average_ticket_price=None  # Setting to null as requested
                )
                db.session.add(concert)
        
        # Commit all changes
        db.session.commit()
        print("Concert data loaded successfully!")

if __name__ == "__main__":
    load_concert_data() 