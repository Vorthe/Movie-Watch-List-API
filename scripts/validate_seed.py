"""
scripts/validate_seed.py

Validate movies_seed_250.json against the current movies table schema.

Checks:
  - Exactly 250 entries
  - title, description, genre are non-empty strings within length limits
  - external_rating is a float in [0, 10]
  - external_id is a non-empty string
  - external_source is "tmdb"
  - external_id values are unique (no duplicates)

Run from repo root:  python scripts/validate_seed.py
"""

import json
import sys

SEED_FILE = "movies_seed_250.json"
EXPECTED_COUNT = 250

TITLE_MAX = 200
DESCRIPTION_MAX = 200
GENRE_MAX = 50
EXTERNAL_ID_MAX = 50
EXTERNAL_SOURCE_MAX = 20


def validate(data: list[dict]) -> list[str]:
    errors: list[str] = []

    if len(data) != EXPECTED_COUNT:
        errors.append(f"Expected {EXPECTED_COUNT} movies, got {len(data)}.")

    seen_external_ids: set[str] = set()

    for i, movie in enumerate(data):
        prefix = f"[{i}] {movie.get('title', '<no title>')!r}"

        title = movie.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{prefix}: title is missing or empty.")
        elif len(title) > TITLE_MAX:
            errors.append(f"{prefix}: title exceeds {TITLE_MAX} chars ({len(title)}).")

        description = movie.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{prefix}: description is missing or empty.")
        elif len(description) > DESCRIPTION_MAX:
            errors.append(
                f"{prefix}: description exceeds {DESCRIPTION_MAX} chars "
                f"({len(description)})."
            )

        genre = movie.get("genre")
        if not isinstance(genre, str) or not genre.strip():
            errors.append(f"{prefix}: genre is missing or empty.")
        elif len(genre) > GENRE_MAX:
            errors.append(f"{prefix}: genre exceeds {GENRE_MAX} chars ({len(genre)}).")

        rating = movie.get("external_rating")
        if not isinstance(rating, (int, float)):
            errors.append(f"{prefix}: external_rating must be numeric.")
        elif not (0 <= rating <= 10):
            errors.append(f"{prefix}: external_rating {rating} out of range [0, 10].")

        external_id = movie.get("external_id")
        if not isinstance(external_id, str) or not external_id.strip():
            errors.append(f"{prefix}: external_id is missing or empty.")
        elif len(external_id) > EXTERNAL_ID_MAX:
            errors.append(f"{prefix}: external_id exceeds {EXTERNAL_ID_MAX} chars.")
        elif external_id in seen_external_ids:
            errors.append(f"{prefix}: duplicate external_id {external_id!r}.")
        else:
            seen_external_ids.add(external_id)

        external_source = movie.get("external_source")
        if not isinstance(external_source, str) or not external_source.strip():
            errors.append(f"{prefix}: external_source is missing or empty.")
        elif len(external_source) > EXTERNAL_SOURCE_MAX:
            errors.append(
                f"{prefix}: external_source exceeds " f"{EXTERNAL_SOURCE_MAX} chars."
            )
        elif external_source != "tmdb":
            errors.append(f"{prefix}: unexpected external_source {external_source!r}.")

    return errors


def main() -> None:
    print(f"Reading {SEED_FILE}...")
    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} entries. Validating...")
    errors = validate(data)

    if errors:
        print(f"\n{len(errors)} validation error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"OK. {len(data)} movies are valid.")


if __name__ == "__main__":
    main()
