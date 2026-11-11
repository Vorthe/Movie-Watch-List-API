"""
Celery tasks.

Import celery_app from celery_app.py and define tasks with @celery_app.task.
"""

from datetime import date

from .celery_app import celery_app


@celery_app.task(name="health.ping")
def ping():
    """Trivial task to verify the worker is running."""
    return "pong"


@celery_app.task(name="notifications.send_welcome")
def send_welcome_notification(user_id: int):
    """Create a welcome notification and send a welcome email.

    In-app notification is always created.
    Email is best-effort: if it fails, we log and continue.
    """
    import logging
    import os

    import resend

    from .database import SessionLocal
    from .models import Notification, Users

    logger = logging.getLogger(__name__)

    db = SessionLocal()
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            return None

        # 1. In-app notification (always)
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

        # 2. Email (best effort)
        api_key = os.getenv("RESEND_API_KEY")
        from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

        if api_key and from_email:
            try:
                resend.api_key = api_key
                resend.Emails.send(
                    {
                        "from": from_email,
                        "to": user.email,
                        "subject": "Welcome to Movie Watch List",
                        "html": (
                            f"<h1>Welcome, {user.first_name}!</h1>"
                            "<p>Thanks for joining Movie Watch List.</p>"
                            "<p>Start by rating a few movies in the catalog.</p>"
                        ),
                    }
                )
                logger.info(
                    f"Welcome email sent to {user.email} "
                    f"(notification id={notification.id})"
                )
            except Exception as e:
                logger.warning(f"Failed to send email to {user.email}: {e}")

        return notification.id
    finally:
        db.close()


@celery_app.task(name="schedule.check_today")
def check_todays_schedules():
    """Create notifications for today's pending schedules.

    Runs daily via Celery Beat. For each schedule that is scheduled for
    today and still pending, create an in-app notification reminding
    the user to watch the movie.

    Returns the number of notifications created.
    """
    from .database import SessionLocal
    from .models import Movie, Notification, WatchSchedule

    today = date.today()
    db = SessionLocal()
    try:
        schedules = (
            db.query(WatchSchedule)
            .filter(
                WatchSchedule.scheduled_date == today,
                WatchSchedule.status == "pending",
            )
            .all()
        )

        created = 0
        for schedule in schedules:
            movie = db.query(Movie).filter(Movie.id == schedule.movie_id).first()
            if movie is None:
                continue

            notification = Notification(
                user_id=schedule.user_id,
                message=(
                    f"Today's movie: {movie.title}. "
                    "Enjoy, and mark it as done when finished."
                ),
            )
            db.add(notification)
            created += 1

        db.commit()
        return {"checked": len(schedules), "notifications_created": created}
    finally:
        db.close()
