from app import db
from sqlalchemy.sql import func


class Rooms(db.Model):

    __tablename__ = 'rooms'

    room_id = db.Column(db.String(255), primary_key=True)
    is_active = db.Column(db.Boolean)
    is_open = db.Column(db.Boolean)
    number_of_users = db.Column(db.Integer)
    game_reset_initiated = db.Column(db.Boolean, default=False)
    game_reset_votes = db.Column(db.Integer, nullable=False, default=0)
    last_activity_check = db.Column(db.DateTime, server_default=func.now())
