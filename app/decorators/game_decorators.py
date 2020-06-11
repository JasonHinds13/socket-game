import functools

from app.models.rooms import Rooms
from flask_socketio import emit
from flask import request


def active_room_required(function):

    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        room_data = args[0] if len(args) > 0 else kwargs['data']
        room = Rooms.query.filter_by(room_id=room_data['roomid']).first()

        if room is None:
            room_data["error"] = "This room does not exist."
            emit('room_error', room_data, room=request.sid)
            return ''
        if room.is_open:
            return function(*args, **kwargs)
        else:
            room_data["error"] = "This room was closed due to player inactivity."
            emit('room_error', room_data, room=request.sid)
            return ''

    return wrapper
