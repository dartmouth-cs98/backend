# hindsite backend

## Description

This repo contains the logic of our server that will save browsing and categorization data to our database. It is what is/will be deployed to Heroku in order for our users to access and store their data. A list of API calls are available at https://github.com/HindsightTwentyTwenty/backend/wiki/API-Doc

## Architecture

Python Django REST API Framework

The code is organized into two directories, hindsite and history. The hindsite directory contains importantly
the settings.py file which has all of the necessary pieces of information for the app to run in Django. The history
directory contains the models that our app uses as well as the views and corresponding routing which is where
all of the logic for the API calls is stored. Finally, the requirements.txt file contains all of the external
packages that are installed for our app to run. The important libraries are django-restframework which simplifies
the REST calls and pytz for better time management.

## Setup

make sure you have python3 installed by calling `which python3` in terminal and copy the path returned
create virtual env: 
```
virtualenv env -p [path to python3]
source env/bin/activate
pip install -r requirements.txt
```

## Deployment

after initial setup, to start virtual env: `source env/bin/activate`

start server: `python manage.py runserver`

make migrations: `python manage.py makemigrations`

migrate: `python manage.py migrate`

shell: `python manage.py shell`

close virtual env: `deactivate`

## Authors

Grace Miller

Shelley Garg

Tommy Kiernan

Wanda Czerwinski

Zach Tannenbaum

## Acknowledgments
