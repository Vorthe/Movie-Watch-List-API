# Phase 2 — Real Data

Replace the 75 fake movies with 250 real ones from TMDB.
Keep the existing lazy join architecture.

Fake data with "IMDb Top Movie" repeated 75 times looks like a toy.
Real titles, real descriptions, and real IMDb scores make the app
feel like a product.

## Decisions

- **One-time fetch, not runtime.** The JSON is committed to git.
  No network calls in production. If TMDB is down, the app still works.

- **Manual seed, not automatic.** seed_production.py runs by hand
  from Render Shell. No hook in start.py. Reason: safer, easier to
  debug, no risk of re-seeding on every boot.

- **Idempotent seed.** Uses external_source + external_id unique key
  (uq_movie_external). Safe to run twice. If a movie already exists,
  skip it. No duplicates.

## Tasks

- [ ] Update scripts/fetch_movies.py
      Save external_rating, external_id, external_source per movie
- [ ] Re-run fetch to regenerate movies_seed_250.json
- [ ] Update scripts/validate_seed.py for new fields
- [ ] Write scripts/seed_production.py
      Bulk insert with ON CONFLICT DO NOTHING
- [ ] Test locally
      Delete fake movies (external_source IS NULL), run seed, check via curl
- [ ] Push and deploy to Render
- [ ] Run seed on Render via Shell
- [ ] Delete test users (testuser, prodtest)
- [ ] End-to-end test on production frontend
- [ ] Update README and KNOWN_ISSUES

## Files

- scripts/fetch_movies.py (update)
- scripts/validate_seed.py (update)
- scripts/seed_production.py (new)
- movies_seed_250.json (regenerated)
- README.md
- docs/KNOWN_ISSUES.md

## Done when

- 250 movies in production DB
- Each has real title, description, genre, external_rating, external_id
- external_source = "tmdb"
- A new user sees real movies, no "IMDb Top Movie" text
- 37 tests still pass
