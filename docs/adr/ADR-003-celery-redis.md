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
- Two new services in local dev: Redis and a Celery worker (via docker-compose).

### Where the worker runs

The worker runs **locally** (on the developer's machine), connected to
Render's Key Value instance via its External URL. It also connects to
Render's PostgreSQL via its External Database URL.

This is a deliberate choice:

1. **Render's Background Worker is not free.** It requires a Starter plan
   (~$7/month). For a portfolio project, we avoid recurring costs.
2. **The worker is not critical for the demo.** When the demo is shown,
   the local worker is started in a terminal. When not needed, it is
   stopped. Zero cost.
3. **The trade-off is acceptable.** The production Web Service still
   works without the worker. Signup succeeds. Notifications are queued
   but not processed until a worker is running.

For a real production deployment with paying users, the worker would
run on a paid instance (Render Worker, Fly.io, Railway, etc.). The code
is identical; only the deployment changes.

### SSRF safety note

The `CELERY_BROKER_URL` on Render uses the internal URL, so traffic
between Web Service and Key Value never leaves Render's private network.
The local worker uses the external URL with TLS (`rediss://`), with
`ssl_cert_reqs=CERT_NONE` only for the local dev certificate. In a real
production setup, use `CERT_REQUIRED` with a proper CA bundle.
