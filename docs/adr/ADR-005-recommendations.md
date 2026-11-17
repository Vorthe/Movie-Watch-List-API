# ADR-005 — Movie Recommendations

## Context

Users want movie suggestions based on what they like.

## Decision

Recommend movies by genre.

How it works:

- User rates some movies.
- We find the top 3 genres from their high ratings (7+).
- We show them other movies in those genres they have not seen,
  sorted by IMDb rating.

Example: if a user rates Matrix and Inception with 9, we recommend
other Sci-Fi movies with high IMDb scores.

If the user has rated less than 3 movies, we show a message:
"Rate at least 3 movies to get recommendations."

## Why not other methods

- Collaborative filtering needs many users. We don't have that.
- Machine learning models need training data. Too much for 250 movies.
- LLMs can invent movies that don't exist in our catalog.

## Consequences

- Simple. No training, no batch jobs.
- Works for any user with 3+ ratings.
- Recommendations are popular movies, not hidden gems.
  This is fine for now.
