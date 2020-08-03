from app import db


class Persons(db.Model):

    __tablename__ = 'persons'

    player_name = db.Column(db.String(255), primary_key=True)
    current_room = db.Column(db.String(255), db.ForeignKey('rooms.room_id'), primary_key=True)
    game_points = db.Column(db.String(255), default=0)
    game_reset_vote = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime)
