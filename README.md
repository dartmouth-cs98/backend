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


### Set Up virtual env: 
make sure you have python3 installed by calling `which python3` in terminal and copy the path returned
`virtualenv env -p [path to python3]`

Before starting your virtualenv, you'll need to set environment variables, so open `env/bin/activate` and under `deactivate()` put:
```
unset DATABASE_NAME
unset DATABASE_USER
unset DATABASE_PASSWORD
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
```

And at the very bottom of the same file put:
```
export DATABASE_NAME='master'
export DATABASE_USER='hindsite'
export DATABASE_PASSWORD='twenty20'
export AWS_ACCESS_KEY_ID='???????????'
export AWS_SECRET_ACCESS_KEY=??????????'
```

Now we can run:

```
source env/bin/activate
pip install -r requirements.txt
```

### For Postgres DB:

Download postgres here and follow the download instructions: https://github.com/PostgresApp/PostgresApp/releases/download/v2.0.2/Postgres-2.0.2.dmg

Make sure that Postgres is open (there should be an elephant on top of your screen. Then on the command line:
```
createdb master
psql -c "CREATE USER hindsite WITH PASSWORD 'twenty20';"
```

### For elastic search:
Download elasticsearch version 2.3.3 here: https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/zip/elasticsearch/2.3.3/elasticsearch-2.3.3.zip

you'll need to unzip it twice in order to make two separate folders, one called `elasticsearch-2.3.3` and the other called `elasticsearch-2.3.3-1`

In each folder you'll open `elasticsearch-2.3.3[-1]/config/elasticsearch.yml` and edit the following:
`cluster.name: hindsite`

To run each of these in the background, enter `elasticsearch-2.3.3[-1]` and run `./bin/elasticsearch -d` to run as a daemon


### For your celery workers:
```
brew install rabbit-mq
```
add `export PATH=$PATH:/usr/local/sbin` to your `.bash_profile`, then:

```
sudo rabbitmq-server -detached
sudo rabbitmqctl add_user hindsite hindsite
sudo rabbitmqctl add_vhost myvhost
sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
```

## Deploy your server and workers:
For each of the following you will need to be in your virtualenv, so if you aren't already, to start virtual env: 
`source env/bin/activate`

The first time after setting up, you'll need to run:
`python manage.py migrate`

To run the server, run:
`python manage.py runserver`

Now to run the workers, in a separate window from your server run:
`python manage.py celery worker -B -l debug --concurrency=2 --without-gossip --without-mingle --without-heartbeat`


### Tools

after initial setup, to start virtual env: `source env/bin/activate`

start server: `python manage.py runserver`

make migrations: `python manage.py makemigrations`

migrate: `python manage.py migrate`

shell: `python manage.py shell_plus`

close virtual env: `deactivate`

## Authors

Grace Miller

Shelley Garg

Tommy Kiernan

Wanda Czerwinski

Zach Tannenbaum

## Acknowledgments
Please see requirements.txt to see list of dependencies for this project.
