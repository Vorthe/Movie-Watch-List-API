"""
scripts/fetch_movies.py

Fetch 250 top-rated movies from TMDB and save them as a JSON seed file.

Run this script ONCE (locally) to generate movies_seed_250.json.
After that, the JSON is committed to git and the project no longer
needs TMDB or an API key at runtime.
"""

import os
import sys
import json
import time

import requests
from dotenv import load_dotenv

# --- Configuration ---
TMDB_BASE_URL = "https://api.themoviedb.org/3"
OUTPUT_FILE = "movies_seed_250.json"
TARGET_MOVIE_COUNT = 250


def load_api_key() -> str:
    """Read TMDB_API_KEY from environment. Exit with error if missing."""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("ERROR: TMDB_API_KEY not found in environment.", file=sys.stderr)
        print("Add it to your .env file (see .env.example).", file=sys.stderr)
        sys.exit(1)
    return api_key


def _request_json(url: str, params: dict, max_retries: int = 3) -> dict:
    """GET a URL and return parsed JSON.

    Retries on timeout, connection errors (including SSL), and 429.
    Uses exponential backoff between attempts.
    """
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
        except (requests.Timeout, requests.ConnectionError) as e:
            last_error = e
            wait = 2**attempt  # 2, 4, 8 seconds
            print(
                f"Network error (attempt {attempt}/{max_retries}): "
                f"{type(e).__name__}. Retrying in {wait}s...",
                file=sys.stderr,
            )
            time.sleep(wait)
            continue

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "5"))
            last_error = requests.HTTPError("429 Too Many Requests")
            print(
                f"Rate limited (attempt {attempt}/{max_retries}). "
                f"Sleeping {retry_after}s...",
                file=sys.stderr,
            )
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        return response.json()

    # If we get here, all retries failed
    assert last_error is not None
    raise last_error


def fetch_genre_map(api_key: str) -> dict[int, str]:
    """Return {genre_id: genre_name} for all TMDB movie genres."""
    data = _request_json(
        f"{TMDB_BASE_URL}/genre/movie/list",
        params={"api_key": api_key},
    )
    return {g["id"]: g["name"] for g in data["genres"]}


def fetch_top_rated(api_key: str, target: int = TARGET_MOVIE_COUNT) -> list[dict]:
    """Fetch up to `target` top-rated movies, one page at a time.

    Stops early if TMDB runs out of pages (rare, but possible).
    Returns raw TMDB movie dicts — normalization happens later.
    """
    movies: list[dict] = []
    page = 1
    total_pages = 1  # will be updated from first response

    while len(movies) < target and page <= total_pages:
        print(f"Fetching page {page} (collected {len(movies)}/{target})...")
        data = _request_json(
            f"{TMDB_BASE_URL}/movie/top_rated",
            params={"api_key": api_key, "page": page},
        )
        total_pages = data["total_pages"]
        movies.extend(data["results"])
        page += 1

    # Trim overshoot: page-based APIs may give us a few extra
    return movies[:target]


def normalize_movie(raw: dict, genre_map: dict[int, str]) -> dict:
    """Convert a raw TMDB movie dict into the project's seed schema.

    Enforces all project constraints:
      - title, description: <= 200 characters (truncated)
      - rating: integer, clamped to [1, 10]
      - genre: always non-empty (falls back to "Unknown")
      - watched: False
      - owner_id: 1
    """
    # --- title: required, max 200 chars ---
    title = (raw.get("title") or "Untitled").strip()[:200]

    # --- description: from overview, max 200 chars, never empty ---
    description = (raw.get("overview") or "").strip()[:200]
    if not description:
        description = "No description available."

    # --- rating: round float, clamp to [1, 10] ---
    rating = round(raw.get("vote_average") or 0)
    rating = max(1, min(10, rating))

    # --- genre: first known genre from genre_ids ---
    genre_ids = raw.get("genre_ids") or []
    genre = next(
        (genre_map[gid] for gid in genre_ids if gid in genre_map),
        "Unknown",
    )

    return {
        "title": title,
        "description": description,
        "rating": rating,
        "watched": False,
        "genre": genre,
        "owner_id": 1,
    }


def save_movies(movies: list[dict], output_path: str) -> None:
    """Write movies to a JSON file (pretty-printed, UTF-8)."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)
        f.write("\n")  # POSIX convention: files end with a newline


def main() -> None:
    load_dotenv()
    api_key = load_api_key()

    print("Fetching genre map...")
    genre_map = fetch_genre_map(api_key)
    print(f"Loaded {len(genre_map)} genres.")

    print("\nFetching top-rated movies...")
    raw_movies = fetch_top_rated(api_key)
    print(f"\nFetched {len(raw_movies)} raw movies.")

    print("\nNormalizing...")
    movies = [normalize_movie(m, genre_map) for m in raw_movies]
    print(f"Normalized {len(movies)} movies.")

    print(f"\nWriting to {OUTPUT_FILE}...")
    save_movies(movies, OUTPUT_FILE)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"Done. Wrote {len(movies)} movies ({size_kb:.1f} KB) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
