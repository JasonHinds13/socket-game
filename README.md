# Socket Game
An online adaptation of the party game Cards Against Humanity.

## Config
### Using Environment Variables
Set the `USE_ENV_VAR` environment variable to True and set the following environment variables to configure the
application. 

#### Environment Variables
* `DATABASE_URL`:  database url in the format for `DB_DRIVER://USERNAME:PASSWORD@DB_HOST/DATABASE`
* `SECRET`: Secret key for encryption

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

## Database setup
Run the following commands to create the database tables:  
* `python flask-migrate.py init`
* `python flask-migrate.py migrate`
* `python flask-migrate.py upgrade`

## Startup Commands
* `virtualenv venv`  
* `source venv/bin/activate` (linux or mac) / `venv\Scripts\activate`
* `pip install -r requirements.txt`  
* `python run.py`
