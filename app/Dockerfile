FROM python:3.11-slim

# OS deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates gnupg && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js (for Tailwind build)
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update -y && apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

ENV APP_ROOT=/srv/chaoticnexus
WORKDIR ${APP_ROOT}

# Install Python dependencies early for better build caching
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Pre-copy frontend manifests for better npm cache
COPY app/package.json ${APP_ROOT}/app/package.json
COPY app/package-lock.json ${APP_ROOT}/app/package-lock.json
WORKDIR ${APP_ROOT}/app
RUN if [ -f package.json ]; then npm ci --no-audit --no-fund; fi

WORKDIR ${APP_ROOT}

# Bring in the application source
COPY app ${APP_ROOT}/app
COPY migrations ${APP_ROOT}/migrations

# Build Tailwind CSS (outputs to app/static/css)
WORKDIR ${APP_ROOT}/app
RUN if [ -f package.json ]; then npm run --silent build:servercss || npm run build:servercss; fi && \
    rm -rf node_modules

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
