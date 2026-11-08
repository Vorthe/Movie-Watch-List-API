# ADR-003 — Celery + Redis for Background Tasks

## Context

Some operations in the app take too long to run during an HTTP request.

Two concrete cases:

1. When a user signs up, we want to send a welcome email.
   SMTP calls take 3-10 seconds. Keeping the HTTP request open that long
   is bad UX and risks timeout.

2. Users can schedule movies to watch on specific dates.
   Every morning we need to check who has movies scheduled for today
   and create a notification for them. This must run without a user
   triggering it.

We need a way to run work outside the request lifecycle, and to run
scheduled work automatically.

## Decision

Use Celery as the task queue, with Redis as the broker.

- Celery handles both background tasks (welcome email) and scheduled
  tasks (daily notification check via Celery Beat).
- Redis is the message broker between FastAPI and Celery workers.
  It is also used as the result backend for task status.

## Consequences

- Signup returns immediately. Email runs in the background.
- Scheduled notifications work even when nobody is using the app.
- Two new services in production: Redis and a Celery worker.
