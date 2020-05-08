from app import db


class Persons(db.Model):

    __tablename__ = 'persons'

    player_name = db.Column(db.String(255), primary_key=True)
    current_room = db.Column(db.String(255), primary_key=True)
    game_points = db.Column(db.String(255), default=0)
    last_active = db.Column(db.DateTime)
