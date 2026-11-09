"""
Celery tasks.

Import celery_app from celery_app.py and define tasks with @celery_app.task.
"""

from .celery_app import celery_app


@celery_app.task(name="health.ping")
def ping():
    """Trivial task to verify the worker is running."""
    return "pong"


@celery_app.task(name="notifications.send_welcome")
def send_welcome_notification(user_id: int):
    """Create a welcome notification for a newly registered user.

    Runs in the Celery worker (separate process), so it opens its own
    database session. Returns the notification id on success, or None
    if the user does not exist.
    """
    # Lazy imports to avoid circular import at module load time
    from .database import SessionLocal
    from .models import Notification, Users

    db = SessionLocal()
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            return None

        notification = Notification(
            user_id=user_id,
            message=(
                f"Welcome to Movie Watch List, {user.first_name}! "
                "Start by rating a few movies."
            ),
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification.id
    finally:
        db.close()
