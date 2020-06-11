from app import db, app
from app.models.rooms import Rooms
from app.models.players import Persons

from sqlalchemy.exc import SQLAlchemyError

from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta


def deactivate_rooms():

    now = datetime.now()
    back_off_time = now - timedelta(minutes=int(app.config["ROOM_BACK_OFF"]))
    inactive_player_time = now - timedelta(minutes=int(app.config["PLAYER_INACTIVITY"]))
    rooms_to_deactivate = []

    app.logger.debug('starting deactivation check. Room back-off -> {}, Player inactivity -> {}'.format(5, 5))

    rooms_to_check = Rooms.query.filter(Rooms.last_activity_check <= str(back_off_time), Rooms.is_active == 'True').all()

    for room in rooms_to_check:
        players = Persons.query.filter_by(current_room=room.room_id).all()

        inactive_players = filter(lambda player: player.last_active <= inactive_player_time, players)

        if len(list(inactive_players)) == len(players):
            app.logger.debug('Room_id -> {} to be marked inactive'.format(room.room_id))
            room.is_active = False
            room.is_open = False
            rooms_to_deactivate.append(room)
        room.last_activity_check = datetime.now()

    if len(rooms_to_deactivate) > 0:
        try:
            db.session.bulk_save_objects(rooms_to_deactivate)
            db.session.commit()
            app.logger.debug('Rooms marked inactive')
        except SQLAlchemyError as e:
            app.logger.warn('DB error: {}'.format(str(e)))
            db.session.rollback()
    else:
        app.logger.debug('No rooms marked inactive')


def initiate_schedule(*args):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(deactivate_rooms, 'interval', minutes=int(args[0]))

    sched.start()
