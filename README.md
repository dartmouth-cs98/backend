# hindsite backend

## Description

This repo contains the logic of our server that will save browsing and categorization data to our database. It is deployed to Heroku and in use for our extension in the Chrome Store. A list of API calls are available at https://github.com/HindsightTwentyTwenty/backend/wiki/API-Doc

## Architecture

Python Django REST API Framework

The code is organized into four main directories, hindsite, history, authentication and search. The hindsite directory contains
importantly the settings.py file which has all of the necessary pieces of information for the app to run in Django. This directory
also contains the static files that make up our website hosted at www.hindsitehistory.com. The history directory contains the 
models that our app uses to store users' history as well as the views and corresponding routing which is where all of the logic for
the API calls are stored. The authentication directory contains our CustomUser model which is used for users. This model stores the
email, hashed password, name, statistics and tracking info for each user. The last directory, search, contains the views and logic 
for our search functionality using elasticsearch. Finally, the requirements.txt file contains all of the external packages that are
installed for our app to run. The important libraries are django-restframework, pytz, celery, beautifulsoup4, boto3, requests, and 
ipython.

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
export AWS_SECRET_ACCESS_KEY='??????????'
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

### The following are our dependencies:
 - amqp v1.4.9
 - anyjson v0.3.3
 - appnope v0.1.0
 - beautifulsoup4 v4.5.3
 - billiard v3.3.0.23
 - boto3 v1.4.4
 - botocore v1.5.12
 - breadability v0.1.20
 - celery v3.1.25
 - chardet v2.3.0
 - decorator v4.0.10
 - dj-database-url v0.4.1
 - Django v1.10.2
 - django-celery v3.2.1
 - django-cors-headers v1.2.2
 - django-extensions v1.7.4
 - djangorestframework v3.4.7
 - docopt v0.6.2
 - docutils v0.13.1
 - gunicorn v19.6.0
 - ipdb v0.10.1
 - ipython v5.1.0
 - ipython-genutils v0.1.0
 - jmespath v0.9.1
 - kombu v3.0.37
 - lxml v3.7.2
 - nltk v3.2.2
 - numpy v1.12.0
 - pexpect v4.2.1
 - pickleshare v0.7.4
 - prompt-toolkit v1.0.8
 - psycopg2 v2.6.2
 - ptyprocess v0.5.1
 - pycrypto v2.6.1
 - Pygments v2.1.3
 - python-dateutil v2.6.0
 - pytz v2016.7
 - requests v2.12.4
 - s3transfer v0.1.10
 - simplegeneric v0.8.1
 - six v1.10.0
 - traitlets v4.3.1
 - vine v1.1.3
 - wcwidth v0.1.7
 - whitenoise v3.2.2
