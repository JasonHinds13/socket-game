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
from sqlalchemy.exc import SQLAlchemyError

from app.cardHandler import getRandomQuestion, getAnswerCards

from app.decorators.game_decorators import active_room_required

users = {}

@app.route('/')
def home():
	return render_template("index.html")

@socketio.on('message')
@active_room_required
@cross_origin(app)
def handleMessage(data):
	player = Persons.query.filter_by(player_name=data['username'], current_room=data['roomid']).first()
	player.last_active = datetime.now()

	try:
		db.session.add(player)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -- DB error: {}'.format(data['username'], data['roomid'], str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	emit('message', data, room=data['roomid'])
	return ''

@socketio.on('join_room')
@cross_origin(app)
def on_join(data):
	username = data['username']
	room = data['roomid']
	join_room(room)
	users[username] = request.sid

	app.logger.info('Player [{}] -> Room [{}] -- Attempting to join the room'.format(username, room))

	room_obj = Rooms.query.filter_by(room_id=room).first()
	if room_obj is None:
		new_room = Rooms(room_id=room, is_active=True, is_open=True, number_of_users=1)
	elif room_obj.is_active and room_obj.is_open:
		room_obj.number_of_users += 1
	else:
		app.logger.debug('Player [{}] -> Room [{}] -- Attempted to joined a closed room'.format(username, room))
		emit('room_closed', data, room=request.sid)
		return ''

	person_obj = Persons.query.filter_by(player_name=username, current_room=room).first()

	if person_obj is not None:
		app.logger.debug('Player [{}] -> Room [{}] -- Attempted to join the room twice.'.format(username, room))
		emit('payer_name_duplicate', data, room=room)
		return ''

	person = Persons(player_name=username, current_room=room, game_points=0, last_active=datetime.now())
	try:
		db.session.add(person)
		if room_obj is None:
			db.session.add(new_room)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -- DB error: {}'.format(username, room, str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	data = {"message": username + ' has joined the room.'}
	emit('join_room_message', data, room=room)
	app.logger.info('Player [{}] -> Room [{}] -- Successfully joined the room'.format(username, room))
	return ''


@socketio.on('leave_room')
@active_room_required
@cross_origin(app)
def on_leave(data):
	username = data['username']
	room_id = data['roomid']

	app.logger.info('Player [{}] -> Room [{}] -- Attempting to leave room'.format(username, room_id))

	try:
		if users[username] != request.sid:
			raise KeyError
	except KeyError as e:
		app.logger.debug("Player [{}] -> Room [{}] -- Request from SID [{}] attempted to leave room but was not found".format(username, room_id, request.sid))
		return ''

	leave_room(room_id)

	player = Persons.query.filter_by(player_name=username).first()
	room = Rooms.query.filter_by(room_id=player.current_room).first()
	room.number_of_users -= 1

	if room.number_of_users == 0:
		room.is_active = False
		room.is_open = False

	try:
		db.session.delete(player)
		db.session.add(room)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -- DB error: {}'.format(username, room_id, str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	del users[username]

	new_data = {"message": username + ' has left the room.'}
	emit('leave_room_message', new_data, room=room_id)

	app.logger.info('Player [{}] -> Room [{}] -- Left successfully'.format(username, room_id))

	try:
		db.session.query(CardHistory).filter(CardHistory.player_name == username).delete()
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -- DB error: {}'.format(username, room_id, str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	current_round = Rounds.query.filter_by(room_id=room_id).order_by(Rounds.round_number.desc()).first()
	if current_round is None:
		return ''
	data['round'] = current_round.round_number
	show_card_history(current_round, data)
	return ''

@socketio.on('draw_question')
@active_room_required
@cross_origin(app)
def getQuestion(data):
	question = getRandomQuestion()

	new_round = Rounds(room_id=data["roomid"], question_card_holder=data["username"])
	last_round = Rounds.query.filter_by(room_id=data["roomid"]).order_by(Rounds.round_number.desc()).first()

	current_round_number = last_round.round_number + 1 if last_round is not None else 1

	app.logger.info('Player [{}] -> Room [{}] -> Round [{}] -- Attempting to draw a question card'.format(data['username'], data['roomid'], current_round_number))

	if last_round is not None and new_round.question_card_holder == last_round.question_card_holder:
		app.logger.debug('Player [{}] -> Room [{}] -> Round [{}] -- Attempted to draw two question cards in a row'.format(data['username'], data['roomid'], current_round_number))
		emit('drew_question_last', data, room=data["roomid"])
		return ''

	room = Rooms.query.filter_by(room_id=data["roomid"]).first()

	if room.number_of_users < 2:
		app.logger.debug('Player [{}] -> Room [{}] -> Round [{}] -- Attempted to start a game with only 1 player'.format(data['username'], data['roomid'], current_round_number))
		data["error"] = "Unable to start the game with only 1 player"
		emit('room_error', data, room=data["roomid"])
		return ''

	if last_round is None and room.number_of_users >=2:
		room.is_open = False

	new_round.round_number = current_round_number
	new_round.number_of_answer_cards = question['numAnswers']

	card_history = CardHistory(player_name=data['username'], round_number=new_round.round_number, room_id=data['roomid'], card_played=question['text'], card_type='question')

	player = Persons.query.filter_by(player_name=data['username'], current_room=data['roomid']).first()
	player.last_active = datetime.now()

	try:
		db.session.add(card_history)
		db.session.add(new_round)
		db.session.add(room)
		db.session.add(player)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -> Round [{}] -- DB error: {}'.format(data['username'], data['roomid'], current_round_number, str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	emit('get_question', question, room=data['roomid'])
	app.logger.info('Player [{}] -> Room [{}] -> Round [{}] -- Played question card: [{}]'.format(data['username'], data['roomid'], current_round_number, question))
	return ''

@socketio.on('draw_answers')
@active_room_required
@cross_origin(app)
def getAnswers(data):
	answers = getAnswerCards(data["needed"])
	player = Persons.query.filter_by(player_name=data['username'], current_room=data['roomid']).first()
	player.last_active = datetime.now()

	try:
		db.session.add(player)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -- DB error: {}'.format(data['username'], data['roomid'], str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	emit('get_answers', answers, room=users[data["username"]])
	return ''

@socketio.on('submit_answer')
@active_room_required
@cross_origin(app)
def submit_answer(data):

	current_round = Rounds.query.filter_by(room_id=data["roomid"]).order_by(Rounds.round_number.desc()).first()
	if current_round is None:
		data['error'] = "Unable to submit an answer before the game starts"
		app.logger.debug('Player [{}] -> Room [{}] -> Round [{}] -- Attempted to play an answer cards before the game started'.format(data['username'], data['roomid'], 0))
		emit('room_error', data, room=request.sid)
		return ''

	app.logger.info('Player [{}] -> Room [{}] -> Round [{}] -- Attempting to submit an answer card'.format(data['username'], data['roomid'], current_round.round_number))

	player_cards = CardHistory.query.filter_by(room_id=data['roomid'], player_name=data['username'], round_number=current_round.round_number, card_type='answer').count()
	if player_cards >= current_round.number_of_answer_cards:
		app.logger.debug('Player [{}] -> Room [{}] -> Round [{}] -- Attempted to play more than the required number of answer cards'.format(data['username'], data['roomid'], current_round.round_number))
		emit('submit_answer_failed', data,room=users[data["username"]])
		return ''

	data['round'] = current_round.round_number

	card_played = CardHistory(player_name=data['username'], round_number=current_round.round_number, room_id=data['roomid'], card_played=data['answer'], card_type='answer')

	player = Persons.query.filter_by(player_name=data['username'], current_room=data['roomid']).first()
	player.last_active = datetime.now()

	try:
		db.session.add(card_played)
		db.session.add(player)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -> Round [{}] -- DB error: {}'.format(data['username'], data['roomid'], current_round.round_number, str(e)))
		db.session.rollback()
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	emit('submit_answer_success', data, room=data["roomid"])
	app.logger.info('Player [{}] -> Room [{}] -> Round [{}] -- Submitted an answer card'.format(data['username'], data['roomid'], current_round.round_number))

	show_card_history(current_round, data)
	return ''


def show_card_history(current_round, data):
	plays_played = CardHistory.query.filter_by(room_id=data['roomid'], round_number=current_round.round_number,card_type='answer').with_entities(CardHistory.player_name).distinct().count()
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

		app.logger.info('Room [{}] -> Round [{}] -- Showing played cards'.format(data['roomid'], current_round.round_number))

		emit('show_answer', data_to_show, room=data["roomid"])


@socketio.on('initiate_game_reset')
@active_room_required
@cross_origin(app)
def on_initiate_game_reset(data):
	app.logger.info('Player [{}] -> Room [{}] -- resetting room'.format(data['username'], data['roomid']))

	room = Rooms.query.filter_by(room_id=data['roomid']).first()
	player = Persons.query.filter_by(player_name=data['username']).first()
	current_round = Rounds.query.filter_by(room_id=data['roomid']).order_by(Rounds.round_number.desc()).first()

	if room.game_reset_initiated:
		app.logger.debug('Player [{}] -> Room [{}] -- room reset already in progress'.format(data['username'], data['roomid']))
		data['announcement'] = 'Game reset has already been initiated.'
		emit('game_announcements', data, request.sid)
		return ''
	elif current_round is None:
		app.logger.debug('Player [{}] -> Room [{}] -- no game data to reset'.format(data['username'], data['roomid']))
		data['announcement'] = 'Cannot reset the game before it starts.'
		emit('game_announcements', data, request.sid)
		return ''

	room.game_reset_initiated = True
	room.game_reset_votes = 1
	player.game_reset_vote = True

	try:
		db.session.add(room)
		db.session.add(player)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -> Round [{}] -- DB error: {}'.format(data['username'], data['roomid'], current_round.round_number, str(e)))
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	data['announcement'] = "Game reset initiated by player: {}".format(data['username'])
	emit('game_announcements', data, room=data['roomid'])

	app.logger.debug('Player [{}] -> Room [{}] -> Round [{}] -- game reset successfully initiated'.format(data['username'], data['roomid'], current_round.round_number))
	data['message'] = "Game reset initiated by player: {}. Please respond".format(data['username'])
	emit('game_reset', data, include_self=False, room=data['roomid'])
	return ''


@socketio.on('game_reset')
@active_room_required
@cross_origin(app)
def on_game_reset_vote(data):
	room = Rooms.query.filter_by(room_id=data['roomid']).first()
	current_round = Rounds.query.filter_by(room_id=data['roomid']).order_by(Rounds.round_number.desc()).first()

	if not room.game_reset_initiated:
		app.logger.debug('Player [{}] -> Room [{}] -- room reset not in progress'.format(data['username'], data['roomid']))
		data['announcement'] = 'Game reset not available.'
		emit('game_announcements', data, request.sid)
		return ''
	elif current_round is None:
		app.logger.debug('Player [{}] -> Room [{}] -- no game data to reset'.format(data['username'], data['roomid']))
		data['announcement'] = 'Cannot reset the game before it starts.'
		emit('game_announcements', data, request.sid)
		return ''

	player = Persons.query.filter_by(player_name=data['username']).first()
	player.game_reset_vote = data['reset_choice']
	room.game_reset_votes += 1

	try:
		db.session.add(player)
		db.session.add(room)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn('Player [{}] -> Room [{}] -> Round [{}] -- DB error: {}'.format(data['username'], data['roomid'], current_round.round_number, str(e)))
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return ''

	if room.game_reset_votes < room.number_of_users:
		data['announcement'] = "Waiting for other players to vote"
		emit('game_announcements', data, room=data['roomid'])
		return ''

	if reset_game(data):
		data['announcement'] = "Game has been reset"
		emit('reset_game', None, room=data['roomid'])
	else:
		data['announcement'] = 'The game continues'
	emit('game_announcements', data, room=data['roomid'])

	return ''


def reset_game(data):
	room = Rooms.query.filter_by(room_id=data['roomid']).first()
	current_round = Rounds.query.filter_by(room_id=data['roomid']).order_by(Rounds.round_number.desc()).first()

	reset_votes = Persons.query.filter_by(current_room=data['roomid'], game_reset_vote=True).count()

	return_val = False
	if reset_votes >= room.number_of_users / 2:
		delete_card_history_statement = CardHistory.__table__.delete().where(CardHistory.room_id == room.room_id)
		delete_rounds_statement = Rounds.__table__.delete().where(Rounds.room_id == room.room_id)

		db.session.execute(delete_card_history_statement)
		db.session.execute(delete_rounds_statement)
		return_val = True

	room.game_reset_votes = 0
	room.game_reset_initiated = False

	try:
		db.session.add(room)
		db.session.commit()
	except SQLAlchemyError as e:
		app.logger.warn(
			'Player [{}] -> Room [{}] -> Round [{}] -- DB error: {}'.format(data['username'], data['roomid'], current_round.round_number, str(e)))
		data['error'] = "There was an error, please contact admins"
		emit('room_error', data, room=request.sid)
		return_val = False

	return return_val
