web: gunicorn hindsite.wsgi --keep-alive 5 --log-level debug
worker: python manage.py rqworker default
