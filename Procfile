web: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn hindsite.wsgi
worker: python manage.py celery worker -B -l info --concurrency=2 --without-gossip --without-mingle --without-heartbeat
