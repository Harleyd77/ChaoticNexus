FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure Python can import the src/ package layout
ENV PYTHONPATH=/app/src

EXPOSE 5000
CMD ["/bin/sh","-c","RELOAD=; if [ \"$FLASK_DEBUG\" = \"1\" ] || [ \"$GUNICORN_RELOAD\" = \"1\" ]; then RELOAD=--reload; fi; exec gunicorn $RELOAD -w ${GUNICORN_WORKERS:-4} -b 0.0.0.0:5000 powder_app.main:app"]
