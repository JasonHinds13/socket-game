from app import socketio, app
from flask import render_template, request
from flask_cors import cross_origin
from flask_socketio import emit, join_room, leave_room

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
