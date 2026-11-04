"""
scripts/validate_seed.py

Validate movies_seed_250.json against the project's schema constraints.

Run after fetch_movies.py to confirm the generated seed file is safe
to import into the database.

Exit code 0 = all good. Exit code 1 = validation failed (details on stderr).
"""

import json
import sys

SEED_FILE = "movies_seed_250.json"
EXPECTED_COUNT = 250
MAX_TEXT_LEN = 200
MIN_RATING = 1
MAX_RATING = 10
REQUIRED_FIELDS = {"title", "description", "rating", "watched", "genre", "owner_id"}


def validate(movies: list) -> list[str]:
    """Return list of error messages. Empty list = valid."""
    errors: list[str] = []

    if len(movies) != EXPECTED_COUNT:
        errors.append(f"Expected {EXPECTED_COUNT} movies, got {len(movies)}")

    for i, m in enumerate(movies):
        prefix = f"[{i}]"

        # 1. All required fields present, no extras
        keys = set(m.keys())
        missing = REQUIRED_FIELDS - keys
        extra = keys - REQUIRED_FIELDS
        if missing:
            errors.append(f"{prefix} Missing fields: {missing}")
        if extra:
            errors.append(f"{prefix} Unexpected fields: {extra}")

        # 2. title: non-empty string, <= 200 chars
        title = m.get("title")
        if not isinstance(title, str) or not title:
            errors.append(f"{prefix} Invalid title: {title!r}")
        elif len(title) > MAX_TEXT_LEN:
            errors.append(f"{prefix} title too long: {len(title)} chars")

        # 3. description: non-empty string, <= 200 chars
        desc = m.get("description")
        if not isinstance(desc, str) or not desc:
            errors.append(f"{prefix} Invalid description: {desc!r}")
        elif len(desc) > MAX_TEXT_LEN:
            errors.append(f"{prefix} description too long: {len(desc)} chars")

        # 4. rating: integer in [1, 10]
        rating = m.get("rating")
        if not isinstance(rating, int) or isinstance(rating, bool):
            errors.append(f"{prefix} rating must be int, got {type(rating).__name__}")
        elif not (MIN_RATING <= rating <= MAX_RATING):
            errors.append(f"{prefix} rating out of range: {rating}")

        # 5. watched: exactly False
        if m.get("watched") is not False:
            errors.append(f"{prefix} watched must be False, got {m.get('watched')!r}")

        # 6. genre: non-empty string
        genre = m.get("genre")
        if not isinstance(genre, str) or not genre.strip():
            errors.append(f"{prefix} Invalid genre: {genre!r}")

        # 7. owner_id: exactly 1
        if m.get("owner_id") != 1:
            errors.append(f"{prefix} owner_id must be 1, got {m.get('owner_id')!r}")

    return errors


def main() -> None:
    try:
        with open(SEED_FILE, encoding="utf-8") as f:
            movies = json.load(f)
    except FileNotFoundError:
        print(
            f"ERROR: {SEED_FILE} not found. Run fetch_movies.py first.", file=sys.stderr
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: {SEED_FILE} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(movies, list):
        print(
            f"ERROR: expected a JSON array, got {type(movies).__name__}",
            file=sys.stderr,
        )
        sys.exit(1)

    errors = validate(movies)

    if errors:
        print(f"FAILED: {len(errors)} error(s):", file=sys.stderr)
        for e in errors[:50]:  # cap output
            print(f"  {e}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        sys.exit(1)

    # Success summary
    print(f"✅ {SEED_FILE} is valid.")
    print(f"   Movies: {len(movies)}")
    print(f"   All constraints satisfied:")
    print(f"     - title, description <= {MAX_TEXT_LEN} chars")
    print(f"     - rating in [{MIN_RATING}, {MAX_RATING}] (int)")
    print(f"     - genre non-empty")
    print(f"     - watched == False, owner_id == 1")


if __name__ == "__main__":
    main()
