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
