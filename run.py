from app import socketio, app
from app.scheduler import database_cleanup

database_cleanup.initiate_schedule(app.config['SCHEDULER_ROOM_DEACTIVATION'], app.config['SCHEDULER_ROOM_DELETION'])
socketio.run(app, host='0.0.0.0')
