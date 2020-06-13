# Socket Game
An online adaptation of the party game Cards Against Humanity.

## Config
### Using Environment Variables
Set the `USE_ENV_VAR` environment variable to True and set the following environment variables to configure the
application. 

#### Environment Variables
* `DATABASE_URL`:  Database url in the format for `DB_DRIVER://USERNAME:PASSWORD@DB_HOST/DATABASE`
* `SECRET`: Secret key for encryption
* `ROOM_BACK_OFF`:  Back-off period in minute for checking if a room is active. 
* `PLAYER_INACTIVITY`: Number of minutes all users in a room should be inactive for before deactivating the room
* `SCHEDULER_ROOM_DEACTIVATION`: Interval in minutes between room inactivity check firing

### Using `config.ini`
Make sure the `USE_ENV_VAR` environment variable to False or not set all and set the following in `app/config/config.ini` to configure the
application. Note: you can ignore the `DB_URI` as it will be populated once the other database variables are set.

#### Config Variables
[DATABASE]  
HOST = DB_HOSTNAME   
DB_NAME = DB_NAME  
USERNAME = DB_USER  
PASSWORD = PASSWORD  
DB_PORT = 123  
DB_DRIVER = DRIVER    

[SERVER]  
SECRET = SUPERSECRETKEY

[INTERVALS]
ROOM_BACK_OFF=5  
PLAYER_INACTIVITY=2  
SCHEDULER_ROOM_DEACTIVATION=5  

## Database setup
Run the following commands to create the database tables:  
* `python flask-migrate.py upgrade`

Note: you will need to update the config.ini with your database details before running these commands

## Database Upgrade
Run the following commands when making changes to the database models:
* `python flask-migrate.py db migrate` to add changes to migration folder
* `python flask-migrate.py db upgrade` to reflect changes in database

Note: you will need to update the config.ini with your database details before running these commands

## Startup Commands
* `virtualenv venv`  
* `source venv/bin/activate` (linux or mac) / `venv\Scripts\activate`
* `pip install -r requirements.txt`  
* `python run.py`
