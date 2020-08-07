# Socket Game
An online adaptation of the party game Cards Against Humanity.


## Initialize
## Config
### Using Environment Variables
Set the `USE_ENV_VAR` environment variable to True and set the following environment variables to configure the
application. 

#### Environment Variables
* `DATABASE_URL`:  Database url in the format for `DB_DRIVER://USERNAME:PASSWORD@DB_HOST/DATABASE`
* `SECRET`: Secret key for encryption
* `ROOT_LOG_LEVEL`: Root logging level 
* `DEFAULT_FORMAT`: Format of system logs

### Using `config.ini`
Make sure the `USE_ENV_VAR` environment variable to False or not set all and set the following in `app/config/config.ini` to configure the
application. Note: you can ignore the `DB_URI` as it will be populated once the other database variables are set.

#### Default Config Variables
[DATABASE]  
HOST = DB_HOSTNAME   
DB_NAME = DB_NAME  
USERNAME = DB_USER  
PASSWORD = PASSWORD  
DB_PORT = 123  
DB_DRIVER = DRIVER    

[SERVER]  
SECRET = SUPERSECRETKEY

[LOGGER]
ROOT_LOG_LEVEL=INFO
DEFAULT_FORMAT=[%(asctime)s] %(levelname)8s [%(remote_addr)s] in %(module)s.%(funcName)s: %(message)s


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
