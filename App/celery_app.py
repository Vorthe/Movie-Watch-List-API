"""
Celery application instance.

This module creates the Celery app that both the worker process
and the FastAPI app use. Keep this separate from tasks.py to avoid
circular imports.

Run worker (with beat for scheduled tasks):
  celery -A App.celery_app worker --beat --loglevel=info
"""

import os
import ssl

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "movie_watch_list",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["App.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# برای اتصال rediss:// (SSL) به Redis روی Render
if CELERY_BROKER_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

# Scheduled tasks (Celery Beat).
celery_app.conf.beat_schedule = {
    "check-todays-schedules": {
        "task": "schedule.check_today",
        "schedule": crontab(hour=8, minute=0),
    },
}
