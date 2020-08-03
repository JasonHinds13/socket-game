from app import db


class Rounds(db.Model):

    __tablename__ = "rounds"

    room_id = db.Column(db.String(255), db.ForeignKey('rooms.room_id'), primary_key=True)
    round_number = db.Column(db.Integer, primary_key=True)
    question_card_holder = db.Column(db.String(255))
    number_of_answer_cards = db.Column(db.Integer)
