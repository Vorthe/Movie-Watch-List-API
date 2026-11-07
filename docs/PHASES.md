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

## Phase 2 — Real Data (CURRENT)

Goal: Replace fake data with real TMDB data.

- Update fetch_movies.py to include external_rating, external_id, external_source
- Regenerate movies_seed_250.json with the new fields
- Write seed_production.py for bulk insert
- Decide hook strategy (start.py vs manual)
- Delete old fake data, seed 250 real movies on Render
- Delete test users
- Verify end-to-end on production

## Phase 3 — Async Tasks

Goal: Add background processing.

- Redis and Celery setup
- First real use case (async welcome email on signup)
- Worker service on Render
- ADR for choosing Celery plus Redis

## Phase 4 — Recommendations

Goal: Smart suggestions from user history.

- Build user preference model from ratings
- Simple recommendation algorithm
- "Recommended for you" section
- ADR for algorithm choice

## Phase 5 — Production

Goal: Make it production ready.

- Rate limiting
- Error tracking (Sentry)
- Monitoring and logs
- Database backup strategy
- Performance optimization
