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
from sqlalchemy import func

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

	player = Persons.query.filter_by(player_name=username).first()
	room = Rooms.query.filter_by(room_id=player.current_room).first()
	room.number_of_users -= 1

	if room.number_of_users == 0:
		room.is_active = False
		room.is_open = False

	db.session.delete(player)
	db.session.add(room)
	db.session.commit()

	del users[username]

	data = {"message": username + ' has left the room.'}
	emit('leave_room_message', data, room=room)

@socketio.on('draw_question')
@cross_origin(app)
def getQuestion(data):
	question = getRandomQuestion()

	new_round = Rounds(room_id=data["roomid"], question_card_holder=data["username"])
	last_round = Rounds.query.filter_by(room_id=data["roomid"]).order_by(Rounds.round_number.desc()).first()

	if last_round is not None and new_round.question_card_holder == last_round.question_card_holder:
		emit('drew_question_last', data, room=data["roomid"])
		return

	room = Rooms.query.filter_by(room_id=data["roomid"]).first()

	if room.number_of_users < 2:
		data["error"] = "Unable to start the game with only 1 player"
		emit('room_error', data, room=data["roomid"])
		return

	if last_round is None and room.number_of_users >=2:
		room.is_open = False

	new_round.round_number = last_round.round_number+1 if last_round is not None else 1
	new_round.number_of_answer_cards = question['numAnswers']

	card_history = CardHistory(player_name=data['username'], round_number=new_round.round_number, room_id=data['roomid'], card_played=question['text'], card_type='question')

	db.session.add(card_history)
	db.session.add(new_round)
	db.session.add(room)
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

	current_round = Rounds.query.filter_by(room_id=data["roomid"]).order_by(Rounds.round_number.desc()).first()

	player_cards = CardHistory.query.filter_by(room_id=data['roomid'], player_name=data['username'], round_number=current_round.round_number, card_type='answer').count()
	if player_cards >= current_round.number_of_answer_cards:
		emit('submit_answer_failed', data,room=users[data["username"]])
		return

	data['round'] = current_round.round_number

	card_played = CardHistory(player_name=data['username'], round_number=current_round.round_number, room_id=data['roomid'], card_played=data['answer'], card_type='answer')
	db.session.add(card_played)
	db.session.commit()

	emit('submit_answer_success', data, room=data["roomid"])

	plays_played = CardHistory.query.filter_by(room_id=data['roomid'], round_number=current_round.round_number, card_type='answer').with_entities(CardHistory.player_name).distinct().count()
	players_in_room = Rooms.query.filter_by(room_id=data['roomid']).first().number_of_users

	players_card_count = CardHistory.query.filter_by(room_id=data['roomid'], round_number=data['round'], card_type='answer').with_entities(CardHistory.player_name, func.count(CardHistory.player_name)).group_by(CardHistory.player_name).all()
	all_cards_played = True
	for player_card_history in players_card_count:
		if player_card_history[1] != current_round.number_of_answer_cards:
			all_cards_played = False
			break

	if (plays_played == players_in_room) and all_cards_played:
		cards = CardHistory.query.filter_by(room_id=data['roomid'], round_number=data['round'], card_type='answer').all()
		data_to_show = []

		for card in cards:
			data_to_show.append({'round': data['round'], 'username': card.player_name, 'answer': card.card_played})

		emit('show_answer', data_to_show, room=data["roomid"])
