FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN SECRET_KEY=build-only DEBUG=false python manage.py collectstatic --noinput

RUN useradd --create-home fuatilia && mkdir -p /data/media && chown -R fuatilia /app /data
USER fuatilia
ENV MEDIA_ROOT=/data/media
EXPOSE 8000

# Migrations run on start so a new image upgrades the database before serving.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py createcachetable && gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 3 --access-logfile -"]
