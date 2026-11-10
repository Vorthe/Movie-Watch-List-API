![CI](https://github.com/Vorthe/Movie-Watch-List-API/actions/workflows/ci.yml/badge.svg)

# Movie Watch List API

A full-stack movie tracking application where users manage their personal watch list. Built with FastAPI (backend), Vue 3 (frontend), PostgreSQL, and deployed on Render with a CI/CD pipeline.

## Live Demo

- **Frontend:** https://movie-watch-list-api.onrender.com
- **API Documentation:** https://movies.vorthe.ir/docs

**Note:** The app runs on Render's free tier. If the service has been idle for more than 15 minutes, the first request may take up to 60 seconds while the service wakes up.

## Tech Stack

**Backend**

- Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic
- PostgreSQL 16
- JWT authentication (python-jose, bcrypt)
- Celery 5.4 + Redis 6 (background tasks, scheduled jobs)
- Pytest (55 tests)

**Frontend**

- Vue 3 (Composition API), Vite, Vue Router
- Axios

**DevOps**

- Docker & Docker Compose
- GitHub Actions (CI)
- Render (Web Service + Static Site + PostgreSQL + Key Value)

## Features

- Shared movie catalog with per-user status (no data duplication)
- User registration and login with JWT authentication
- Browse catalog with search, filter, sort, and pagination
- Mark movies as watched / unwatched
- Personal rating (1–10) per user, debounced autosave
- Public rating from TMDB displayed alongside personal rating
- Reset personal status back to "untouched"
- Statistics dashboard (total, watched, unwatched, average of your ratings)
- User profile: change password, update phone number
- Admin panel to manage the catalog (read, create, update, delete)
- In-app notifications (bell in navbar, unread badge, mark as read)
- Watch Schedule: plan movies for specific dates, with daily reminders
- Background tasks via Celery: welcome notification on signup
- Scheduled task via Celery Beat: daily check for today's movies

## Data

The movie catalog contains 250 real movies from TMDB. Each entry has:

- Real title, description, and genre
- IMDb rating (`external_rating`, e.g. 8.7)
- TMDB id (`external_id`) for future syncs

The catalog is committed to git as `movies_seed_250.json`. Runtime does not depend on TMDB — the app still works if TMDB is down.

## Project Structure

```text
Movie-Watch-List-API/
├── App/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── movies.py
│   │   ├── admin.py
│   │   ├── users.py
│   │   ├── notifications.py
│   │   └── schedule.py
│   ├── main.py
│   ├── database.py       # SQLAlchemy engine + session
│   ├── models.py         # Users, Movie, UserMovieStatus, Notification, WatchSchedule
│   ├── celery_app.py     # Celery configuration
│   └── tasks.py          # Background tasks
├── alembic/              # Database migrations
├── tests/                # 55 pytest tests
├── frontend/             # Vue 3 + Vite app
├── docs/
│   ├── OVERVIEW.md
│   ├── PHASES.md
│   ├── ERD.md
│   └── adr/              # Architecture Decision Records
├── scripts/              # TMDB fetch, seed, validation
├── .github/workflows/    # GitHub Actions CI
├── Dockerfile
├── docker-compose.yml
├── start.py              # Startup script (DB wakeup + migrations)
└── requirements.txt
```

## Local Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend)

### Backend

1. Clone the repository:

   ```bash
   git clone https://github.com/Vorthe/Movie-Watch-List-API.git
   cd Movie-Watch-List-API
   ```

2. Create the environment file:

   ```bash
   cp .env.example .env
   ```

   Then fill in the values. For local development:

   ```env
   POSTGRES_DB=moviewatchlist
   POSTGRES_USER=moviewatchlist
   POSTGRES_PASSWORD=moviewatchlist_dev_pass
   DATABASE_URL=postgresql://moviewatchlist:moviewatchlist_dev_pass@db:5432/moviewatchlist
   SECRET_KEY=change_me_in_production
   ALGORITHM=HS256
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   DB_REQUIRE_SSL=false
   REDIS_URL=redis://redis:6379/0
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/1
   TMDB_API_KEY=your_tmdb_api_key_here
   ```

3. Build and start:

   ```bash
   docker compose up --build
   ```

4. The API is available at `http://localhost:8001/docs`.

### Frontend

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Create `frontend/.env.local`:

   ```env
   VITE_API_BASE_URL=http://localhost:8001
   ```

4. Start the dev server:

   ```bash
   npm run dev
   ```

5. Open `http://localhost:5173`.

### Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

### Running the Celery Worker (Development)

The Web Service on Render can enqueue tasks (e.g. welcome notification on signup), but tasks are only executed when a worker is running. In this project, the worker runs **locally** and connects to Render's Redis and PostgreSQL via their External URLs.

1. Get the External URLs from Render:
   - **Key Value** → Connect → External Key Value URL (`rediss://...`)
   - **PostgreSQL** → Connect → External Database URL (`postgresql://...`)

2. Export them in your terminal:

   ```bash
   export EXT_REDIS="rediss://..."
   export EXT_DB="postgresql://..."
   ```

3. Start the worker (from the project root):

   ```bash
   docker compose run --rm \
     -e CELERY_BROKER_URL="${EXT_REDIS}/0" \
     -e CELERY_RESULT_BACKEND="${EXT_REDIS}/0" \
     -e DATABASE_URL="${EXT_DB}" \
     -e DB_REQUIRE_SSL=true \
     worker
   ```

4. You should see `celery@... ready.`. Any task queued by the production Web Service will now be processed.

**Note:** The worker is not needed for basic usage. Without it, signup still succeeds (no 500); only the welcome notification is not created.

## Architecture Notes

### Database Connection Strategy

The backend uses `NullPool` in SQLAlchemy to prevent stale connections to the managed PostgreSQL instance. This is a deliberate choice for environments where the database provider closes idle connections at the network level.

### Lazy Join Data Model

`movies` is a shared catalog. `user_movie_status` holds per-user state (watched, rating). A missing row means the user has not touched the movie. The API joins the two tables only for the current user, so 1,000 users × 250 movies still means 250 catalog rows, not 250,000.

See `docs/adr/ADR-001-lazy-join.md`.

### Dual Rating

Two separate fields:

- `movies.external_rating` — from TMDB (read-only, decimal)
- `user_movie_status.rating` — from the user (1–10, integer)

See `docs/adr/ADR-002-dual-rating.md`.

### Background Tasks

Celery + Redis handle asynchronous work:

- **Welcome notification** — enqueued on signup, runs in background
- **Daily schedule check** — Celery Beat runs `schedule.check_today` every day at 08:00 UTC, creating notifications for today's scheduled movies

See `docs/adr/ADR-003-celery-redis.md` for why Celery + Redis, not Kafka or RabbitMQ.

### Startup Sequence

The application uses `start.py` as its entry point:

1. Waits for the database to be reachable (retry loop with 5s intervals)
2. Runs Alembic migrations
3. Launches Uvicorn

This prevents race conditions on deployment platforms where the database may still be waking up.

### CI Pipeline

Every push to `main` triggers:

1. Python 3.13 environment setup
2. Dependency installation
3. Full test suite (55 tests)

If tests pass, GitHub Actions calls Render's Deploy Hook to deploy the backend. Failures block deployment, ensuring broken code never reaches production.

## Environment Variables

| Variable                | Description                                       | Required |
| ----------------------- | ------------------------------------------------- | -------- |
| `DATABASE_URL`          | PostgreSQL connection string                      | Yes      |
| `SECRET_KEY`            | JWT signing key                                   | Yes      |
| `ALGORITHM`             | JWT algorithm (default: HS256)                    | Yes      |
| `CORS_ORIGINS`          | Comma-separated allowed origins                   | Yes      |
| `DB_REQUIRE_SSL`        | Set to `true` for managed DBs (e.g. Render)       | No       |
| `REDIS_URL`             | Redis connection (used by Celery)                 | Yes      |
| `CELERY_BROKER_URL`     | Celery broker URL                                 | Yes      |
| `CELERY_RESULT_BACKEND` | Celery result backend URL                         | Yes      |
| `VITE_API_BASE_URL`     | Backend URL (frontend only)                       | Yes      |
| `TMDB_API_KEY`          | TMDB API key (only for `scripts/fetch_movies.py`) | No       |

## Architecture Decision Records

- `docs/adr/ADR-001-lazy-join.md` — Shared catalog with per-user status
- `docs/adr/ADR-002-dual-rating.md` — External rating and personal rating
- `docs/adr/ADR-003-celery-redis.md` — Celery + Redis for background tasks

## License

MIT
