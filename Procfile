release: python manage.py migrate --noinput && python manage.py createcachetable
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 3 --access-logfile -
