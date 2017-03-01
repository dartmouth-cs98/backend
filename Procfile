web: gunicorn hindsite.wsgi
worker: python manage.py celery worker -B -l info --without-gossip --without-mingle --without-heartbeat
