# Development Phases

## Phase 0 — Bootstrap (DONE)

Goal: Get a skeleton app running.

- FastAPI with health check
- Docker Compose with PostgreSQL
- Alembic migrations
- Deploy on Render
- Basic JWT auth
- Basic per-user movie CRUD

## Phase 1 — Foundation (CURRENT)

Goal: Refactor to a clean, scalable architecture.

- Lazy join refactor: shared catalog plus per-user status
- Dual rating: external (TMDB) plus personal
- Rewrite all endpoints for new data model
- Rewrite tests
- Rewrite frontend
- Documentation: overview, phases, ERD, ADRs
- CI/CD pipeline with deploy hook

## Phase 2 — Real Data (NEXT)

Goal: Replace fake data with real TMDB data.

- Delete old fake data
- Fetch 250 real movies from TMDB
- Seed script for production
- End-to-end test on Render
- Remove test users

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
