from marshmallow import Schema, fields

class ConcertSchema(Schema):
    class Meta:
        ordered = True
    id = fields.Integer()
    artist = fields.String()
    genres = fields.String()
    date = fields.Date()
    venue = fields.String()
    city = fields.String()
    state = fields.String()
    capacity = fields.Integer()
    number_of_songs = fields.Integer()