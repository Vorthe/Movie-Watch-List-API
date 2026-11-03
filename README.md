![CI](https://github.com/Vorthe/Movie-Watch-List-API/actions/workflows/ci.yml/badge.svg)

# Movie Watch List API

A full-stack movie tracking application where users manage their personal watch list. Built with FastAPI (backend), Vue 3 (frontend), PostgreSQL, and deployed on Render with a CI/CD pipeline.

## Live Demo

- **Frontend:** https://movie-watch-list-api.onrender.com
- **API Documentation:** https://movies.vorthe.ir/docs

## Tech Stack

**Backend**

- Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic
- PostgreSQL 16
- JWT authentication (python-jose, passlib)
- Pytest (28 tests)

**Frontend**

- Vue 3 (Composition API), Vite, Vue Router
- Axios

**DevOps**

- Docker & Docker Compose
- GitHub Actions (CI)
- Render (backend + frontend + database)

## Features

- User registration and login with JWT authentication
- Personal movie watch list (create, read, update, delete)
- Search movies by title
- Filter by watched/unwatched status
- Sort by rating or title
- Pagination (12 movies per page)
- Statistics dashboard: total, watched, unwatched, average rating
- User profile management (change password, update phone number)
- Admin panel with read/delete permissions

## Project Structure

```text
Movie-Watch-List-API/
├── App/
│   ├── routers/          # auth, movies, users, admin
│   ├── main.py
│   ├── database.py       # SQLAlchemy engine + session
│   └── models.py
├── alembic/              # Database migrations
├── tests/                # 28 pytest tests
├── frontend/             # Vue 3 + Vite app
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

## Architecture Notes

### Database Connection Strategy

The backend uses `NullPool` in SQLAlchemy to prevent stale connections to the managed PostgreSQL instance. This is a deliberate choice for environments where the database provider closes idle connections at the network level.

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
3. Full test suite (28 tests)

Failures block deployment, ensuring broken code never reaches production.

## Environment Variables

| Variable            | Description                     | Required |
| ------------------- | ------------------------------- | -------- |
| `DATABASE_URL`      | PostgreSQL connection string    | Yes      |
| `SECRET_KEY`        | JWT signing key                 | Yes      |
| `ALGORITHM`         | JWT algorithm (default: HS256)  | Yes      |
| `CORS_ORIGINS`      | Comma-separated allowed origins | Yes      |
| `VITE_API_BASE_URL` | Backend URL (frontend only)     | Yes      |

## License

MIT
