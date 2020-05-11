from app import db


class CardHistory(db.Model):

    __tablename__ = 'card_history'

    card_played_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_name = db.Column(db.String(255))
    round_number = db.Column(db.Integer)
    room_id = db.Column(db.String(255))
    card_played = db.Column(db.Text)
    card_type = db.Column(db.String(255))
