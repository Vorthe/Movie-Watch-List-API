# Entity Relationship Diagram

The app has three tables: one for users, one for the shared movie
catalog, and one for per-user movie status.

```mermaid
erDiagram
    USERS ||--o{ USER_MOVIE_STATUS : "has statuses"
    MOVIES ||--o{ USER_MOVIE_STATUS : "tracked in"

    USERS {
        int id PK
        string email UK
        string username UK
        string first_name
        string last_name
        string hashed_password
        bool is_active
        string role
        string phone_number
    }

    MOVIES {
        int id PK
        string title
        string description
        string genre
        numeric external_rating
        string external_id
        string external_source
        datetime created_at
    }

    USER_MOVIE_STATUS {
        int id PK
        int user_id FK
        int movie_id FK
        bool watched
        int rating
        datetime created_at
        datetime updated_at
    }
```

## Notes

- `movies` is a shared catalog. It has no owner. One row per movie,
  even if 1000 users track it.
- `user_movie_status` has one row per (user, movie) pair. A missing
  row means the user has not touched the movie yet.
- Both foreign keys use `ON DELETE CASCADE`. Deleting a user removes
  their statuses. Deleting a movie removes statuses for that movie.
- `(user_id, movie_id)` is unique. A user cannot have two statuses
  for the same movie.
