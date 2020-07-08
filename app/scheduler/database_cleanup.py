from app import db, app
from app.models.rooms import Rooms
from app.models.players import Persons
from app.models.cards_played import CardHistory
from app.models.rounds import Rounds

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


def remove_inactive_rooms():
    back_off_time = datetime.now() - timedelta(minutes=int(app.config["ROOM_BACK_OFF"]))

    app.logger.debug('getting inactive rooms')

    rooms_to_remove = Rooms.query.filter(Rooms.last_activity_check <= str(back_off_time), Rooms.is_active == 'False').all()

    for room in rooms_to_remove:
        app.logger.debug('removing room data for room -> {}'.format(room.room_id))
        delete_card_history_statement = CardHistory.__table__.delete().where(CardHistory.room_id == room.room_id)
        delete_players_statement = Persons.__table__.delete().where(Persons.current_room == room.room_id)
        delete_rounds_statement = Rounds.__table__.delete().where(Rounds.room_id == room.room_id)

        db.session.execute(delete_card_history_statement)
        db.session.execute(delete_players_statement)
        db.session.execute(delete_rounds_statement)
        db.session.delete(room)
        app.logger.debug('removed room data for room -> {}'.format(room.room_id))

    db.session.commit()

    if len(rooms_to_remove) > 0:
        app.logger.debug('room data removal committed')
    else:
        app.logger.debug('no room data removal committed')


def initiate_schedule(*args):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(deactivate_rooms, 'interval', minutes=int(args[0]))
    sched.add_job(remove_inactive_rooms, 'interval', minutes=int(args[1]))

    sched.start()
