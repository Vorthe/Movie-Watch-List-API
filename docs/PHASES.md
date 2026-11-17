# Development Phases

## Phase 1 — Foundation (DONE)

Goal: Refactor to a clean, scalable architecture.

- Lazy join refactor: shared catalog plus per-user status
- Dual rating: external (TMDB) plus personal
- Rewrite all endpoints for new data model
- Rewrite tests (37 passing)
- Rewrite frontend with inline status editing
- Documentation: overview, phases, ERD, ADR-001, ADR-002
- CI/CD pipeline with deploy hook

## Phase 2 — Real Data (DONE)

Goal: Replace fake data with real TMDB data.

- Updated fetch_movies.py to filter by vote_count >= 10000
  (avoids obscure movies with few votes)
- Regenerated movies_seed_250.json with real data
  (Shawshank #1, Godfather #2, 12 Angry Men #3)
- Added external_rating, external_id, external_source fields
- Wrote seed_production.py (idempotent, safe to re-run)
- Seeded 250 movies on Render via local terminal
- Cleaned up test users
- Fixed decimal input on rating

## Phase 3 — Async Tasks (DONE)

Goal: Add background processing with Celery + Redis.

- Redis (Render Key Value) as broker and result backend
- Celery Worker (local, connects to Render Redis)
- Celery Beat for daily scheduled tasks
- Welcome notification on signup (async)
- Watch Schedule: users schedule movies for specific dates
- Daily check: notify users about today's scheduled movies
- In-app notifications UI (bell in navbar, full page)
- Schedule management UI (create, update status, delete)
- 55 tests passing (was 44, added 11 for schedule)

## Phase 4 — Production Features (DONE)

Goal: Add production-grade features that separate a portfolio project
from a real product.

- **4.0 — Security:** Removed client-controlled role from signup. Admin
  promotion now requires an admin-only endpoint. Closed KNOWN_ISSUES #8.
- **4.1 — Email:** Real welcome emails via Resend. SendGrid rejected signup
  from Iran; Resend accepted. Email is best-effort (signup succeeds if
  email fails). Domain verification needed for sending to users other than
  account owner.
- **4.2 — Admin panel:** `fastapi-admin-kit` at `/admin`, session auth,
  separate async engine and `admin_users` table. Covers Movie,
  UserMovieStatus, Notification, WatchSchedule.
- **4.3 — Recommendations:** `GET /recommendations` returns top genres from
  user's 7+ ratings and recommends unseen movies in those genres sorted by
  IMDb rating.

## Phase 5 — Production

Goal: Make it production ready.

- Rate limiting
- Error tracking (Sentry)
- Monitoring and logs
- Database backup strategy
- Performance optimization
