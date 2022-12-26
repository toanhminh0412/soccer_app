# Victoria Soccer Application
## About the application
### Description
This application focuses on two main targets - soccer players and soccer groups. For soccer players, the app allows them see information of all the avaible games and join them. For soccer groups, the app allows groups to accept and manage members, post their recurring games and arrange teams for each game.

### Main functionalities
To be written

## Set up and development
This document assumes you are working with Linux operating system
### Clone the Project with HTTPS
    $ git clone https://gitlab.com/uvic-arcsoft/contacts.git

### Create a virtual environment inside the Git project
    $ cd contacts
    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install --upgrade pip     # Upgrade pip
    $ pip install -r requirements.txt   # for getting application required packages

### Configure the application
From the root directotry, run:

    $ touch soccer_app/soccer_app/.env   # Create a file for environment variables
    $ python3 soccer_app/manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())' # Generate a Django SECRET_KEY
    $ go to the soccer_app/soccer_app/.env file, add two lines:
    1. SECRET_KEY=<output_from_the_command_above>
    2. DEBUG=True

### Start up the application
The following command line from the root directory tells Django to run on `localhost` and use port `4001`:

    $ python3 app_starter/manage.py runserver 127.0.0.1:4001
    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).
    September 08, 2022 - 10:01:46
    Django version 4.1.1, using settings 'app_starter.settings'
    Starting development server at http://127.0.0.1:4001/
    Quit the server with CTRL-BREAK.


