from datetime import datetime
from app.models.concert import Concert
from app.models.user_concerts import UsersConcert
from app.extensions import db

def seed_data():
    # Seed concerts
    concert1 = Concert(
            artist="Artist A",
            genres="Rock, Pop",
            date=datetime(2025, 1, 25),
            venue="Venue A",
            city="City A",
            state="State A",
            capacity=1000,
            number_of_songs=20
        )
    concert2 = Concert(
            artist="Artist B",
            genres="Jazz, Blues",
            date=datetime(2025, 2, 15),
            venue="Venue B",
            city="City B",
            state="State B",
            capacity=800,
            number_of_songs=15
        )

    user_concert1 = UsersConcert(
        user_id=1,
        concert_id=concert1.id,
        user_ticket_price=50.0,
        timestamp=datetime(2025, 1, 25)
    )

    db.session.add_all([concert1, concert2, user_concert1, ])
    db.session.commit()
    print("Seed data added successfully!")