from app import socketio, app
from flask import render_template, request
from flask_cors import cross_origin
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

from app import db
from app.models.players import Persons
from app.models.rooms import Rooms
from app.models.rounds import Rounds
from app.models.cards_played import CardHistory

from app.cardHandler import getRandomQuestion, getAnswerCards

users = {}

@app.route('/')
def home():
	return render_template("index.html")

@socketio.on('message')
@cross_origin(app)
def handleMessage(data):
	emit('message', data, room=data['roomid'])

@socketio.on('join_room')
@cross_origin(app)
def on_join(data):
	username = data['username']
	room = data['roomid']
	join_room(room)
	users[username] = request.sid

	room_obj = Rooms.query.filter_by(room_id=room).first()
	if room_obj is None:
		new_room = Rooms(room_id=room, is_active=True, is_open=True, number_of_users=1)
	elif room_obj.is_active and room_obj.is_open:
		room_obj.number_of_users += 1
	else:
		emit('room_closed', data, room=room)
		return

	person_obj = Persons.query.filter_by(player_name=username, current_room=room).first()

	if person_obj is not None:
		emit('payer_name_duplicate', data, room=room)
		return

	person = Persons(player_name=username, current_room=room, game_points=0, last_active=datetime.now())
	db.session.add(person)
	if room_obj is None:
		db.session.add(new_room)
	db.session.commit()

	data = {"message": username + ' has joined the room.'}
	emit('join_room_message', data, room=room)

@socketio.on('leave_room')
@cross_origin(app)
def on_leave(data):
	username = data['username']
	room = data['roomid']
	leave_room(room)
	data = {"message": username + ' has left the room.'}
	emit('leave_room_message', data, room=room)

@socketio.on('draw_question')
@cross_origin(app)
def getQuestion(data):
	question = getRandomQuestion()

	new_round = Rounds(room_id=data["roomid"], question_card_holder=data["username"])
	last_round = Rounds.query.filter_by(room_id=data["roomid"]).order_by(Rounds.round_number.desc()).first()

	if last_round is not None and new_round.question_card_holder == last_round.quequestion_card_holder:
		emit('drew_question_last', data, room=data["roomid"])
		return

	new_round.round_number = last_round.round_number+1 if last_round is not None else 1
	new_round.number_of_answer_cards = question['numAnswers']

	card_history = CardHistory(player_name=data['username'], round_number=new_round.round_number, room_id=data['roomid'], card_played=question['text'], card_type='question')

	db.session.add(card_history)
	db.session.add(new_round)
	db.session.commit()

	emit('get_question', question, room=data['roomid'])

@socketio.on('draw_answers')
@cross_origin(app)
def getAnswers(data):
	answers = getAnswerCards(data["needed"])
	emit('get_answers', answers, room=users[data["username"]])

@socketio.on('submit_answer')
@cross_origin(app)
def submit_answer(data):
	emit('show_answer', data, room=data["roomid"])
