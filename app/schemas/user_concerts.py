from marshmallow import Schema, fields


class UsersConcertSchema(Schema):
    class Meta:
        ordered = True
    id = fields.Integer()
    user_id = fields.String()
    concert_id = fields.Integer()
    user_ticket_price = fields.Float(allow_none=True) 
    timestamp = fields.Date()
