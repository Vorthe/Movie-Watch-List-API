# ADR-002 — Two Separate Ratings

## Context

Users want to give their own opinion about a movie. The movie itself
also has a public rating from TMDB. Mixing them in one field loses
information and creates confusion.

A user should feel that their opinion matters separately from the
crowd.

## Decision

Store two ratings:

1. `movies.external_rating` — decimal, from TMDB (e.g. 8.7). Read-only.
2. `user_movie_status.rating` — integer 1 to 10. Set by the user.

## Consequences

- The frontend shows both: "IMDb 8.7 | You rated 9".
- Public rating is not editable by users.
- User rating is private to each user.
- Recommendations (Phase 4) use only personal ratings.
- Statistics can compare user taste with public opinion.
- Small cost: one more column and a slightly richer API response.
