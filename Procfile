web: gunicorn hindsite.wsgi
worker: python manage.py celery worker -B -l info --concurrency=2 --without-gossip --without-mingle --without-heartbeat
