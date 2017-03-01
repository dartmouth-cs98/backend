web: gunicorn hindsite.wsgi
worker: python manage.py celery worker -B --concurrency=3 --without-gossip --without-mingle --without-heartbeat
