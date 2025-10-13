FROM python:3.11-slim

# OS deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

ENV APP_ROOT=/srv/chaoticnexus
WORKDIR ${APP_ROOT}

# Install Python dependencies early for better build caching
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Bring in the application source
COPY app ${APP_ROOT}/app
COPY migrations ${APP_ROOT}/migrations

ENV PYTHONPATH=${APP_ROOT}
ENV HOST=0.0.0.0 PORT=8000 WORKERS=3 TIMEOUT=90
EXPOSE 8000

# Migrations (Flask-Migrate or Alembic) then start via gunicorn, with common entrypoint fallbacks
CMD bash -lc ' \
  if [ -f manage.py ]; then \
    python manage.py db upgrade || true; \
  elif [ -d migrations ]; then \
    cd /srv/chaoticnexus && flask db upgrade || true; \
  fi; \
  if [ -f app/gunicorn.conf.py ]; then \
    exec gunicorn -c app/gunicorn.conf.py app.wsgi:app; \
  elif [ -f app/wsgi.py ]; then \
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} app.wsgi:app; \
  else \
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} "app:create_app()"; \
  fi'
