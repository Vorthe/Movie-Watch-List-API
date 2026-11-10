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

## Phase 5 — Production

Goal: Make it production ready.

- Rate limiting
- Error tracking (Sentry)
- Monitoring and logs
- Database backup strategy
- Performance optimization
