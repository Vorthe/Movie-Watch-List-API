"""
scripts/seed_production.py

Seed the movies table with data from movies_seed_250.json.

Behavior:
  1. Delete all movies where external_source IS NULL
     (these are legacy fake movies with no external reference)
  2. Insert 250 movies from the seed file
  3. Skip movies that already exist (by external_source + external_id)
  4. Never touch user_movie_status rows directly
     (CASCADE handles cleanup when movies are deleted)

Safe to run multiple times. Idempotent.

Usage (from repo root):
  python scripts/seed_production.py

On Render (from Shell):
  python scripts/seed_production.py
"""

import json
import os
import sys

# Make the project root importable when running from scripts/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from App.database import SessionLocal
from App.models import Movie

SEED_FILE = "movies_seed_250.json"
EXTERNAL_SOURCE = "tmdb"


def load_seed_data(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def delete_legacy_movies(db) -> int:
    """Delete movies with no external source (old fake data)."""
    legacy = db.query(Movie).filter(Movie.external_source.is_(None)).all()
    count = len(legacy)
    for movie in legacy:
        db.delete(movie)
    db.commit()
    return count


def get_existing_external_ids(db) -> set[str]:
    """Return set of external_id values already in the table."""
    rows = (
        db.query(Movie.external_id)
        .filter(Movie.external_source == EXTERNAL_SOURCE)
        .all()
    )
    return {r[0] for r in rows if r[0] is not None}


def insert_movies(db, movies: list[dict]) -> tuple[int, int]:
    """Insert movies that don't already exist.

    Returns (inserted_count, skipped_count).
    """
    existing = get_existing_external_ids(db)
    inserted = 0
    skipped = 0

    for movie_data in movies:
        ext_id = movie_data["external_id"]
        if ext_id in existing:
            skipped += 1
            continue

        movie = Movie(
            title=movie_data["title"],
            description=movie_data["description"],
            genre=movie_data["genre"],
            external_rating=movie_data["external_rating"],
            external_id=ext_id,
            external_source=movie_data["external_source"],
        )
        db.add(movie)
        inserted += 1

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"ERROR: IntegrityError during insert: {e}", file=sys.stderr)
        raise

    return inserted, skipped


def main() -> None:
    print(f"Reading {SEED_FILE}...")
    movies = load_seed_data(SEED_FILE)
    print(f"Loaded {len(movies)} movies from seed file.")

    db = SessionLocal()
    try:
        print("\nDeleting legacy movies (external_source IS NULL)...")
        deleted = delete_legacy_movies(db)
        print(f"Deleted {deleted} legacy movie(s).")

        print("\nInserting new movies...")
        inserted, skipped = insert_movies(db, movies)
        print(f"Inserted: {inserted}")
        print(f"Skipped (already exist): {skipped}")

        total = db.query(Movie).count()
        print(f"\nTotal movies in database: {total}")
    finally:
        db.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
