"""
Celery tasks.

Import celery_app from celery_app.py and define tasks with @celery_app.task.
"""

from .celery_app import celery_app


@celery_app.task(name="health.ping")
def ping():
    """Trivial task to verify the worker is running."""
    return "pong"
