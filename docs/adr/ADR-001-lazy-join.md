# ADR-001 — Shared Catalog with Per-User Status

## Context

The app supports many users tracking the same movies. A naive design
stores a copy of each movie for every user. With 250 movies and 1000
users this means 250,000 rows. The data inside those rows is 99%
identical: same title, description, and genre. Only the watched flag
and the rating differ.

I also plan to add more data sources later (TMDB, Rotten Tomatoes).
Each new source would multiply the duplication.

## Decision

Split movies into two tables:

1. `movies` — shared catalog. One row per movie. No user ownership.
2. `user_movie_status` — one row per (user, movie) only when the user
   interacts with the movie.

A missing row in `user_movie_status` means the user did not touch the
movie. The API returns all movies with a default empty status.

## Consequences

- No duplication. 250 movies means 250 rows, not 250 × users.
- Adding a new data source is one bulk insert.
- Per-user queries use a simple LEFT JOIN.
- Deleting a user removes all their statuses (CASCADE).
- Deleting a movie removes all statuses for that movie (CASCADE).
- Recommendations become a simple query on user statuses.
- Small cost: the API always joins two tables to build a response.
