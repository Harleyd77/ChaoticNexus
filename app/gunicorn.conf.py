"""Gunicorn configuration for Chaotic Nexus."""

import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count()))
threads = int(os.environ.get("GUNICORN_THREADS", 1))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gthread")
preload_app = True
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 90))
