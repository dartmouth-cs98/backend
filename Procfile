web: gunicorn hindsite.wsgi
worker: python manage.py celery worker -B --concurrency=2 --without-gossip --without-mingle --without-heartbeat
