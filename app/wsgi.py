"""WSGI entry point for Gunicorn within the container."""

from app import create_app

app = create_app()
