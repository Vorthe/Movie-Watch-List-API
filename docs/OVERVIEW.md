# Movie Watch List — Project Overview

## What is this?

A web app for tracking movies. Users can browse a catalog of movies,
mark them as watched, and give personal ratings.

## Who uses it?

- Users: people who want to track what they watched
- Admin: the person who manages the movie catalog

## Problems we solve

- Users forget which movies they watched
- Users want a personal rating separate from IMDb
- Users want to see their viewing stats
- Users want to compare their taste with public scores

## What is in scope

- Shared movie catalog (one copy, not per user)
- User accounts with JWT authentication
- Mark movies as watched or not watched
- Personal rating (1-10) per user
- Public rating from TMDB (display only)
- Search, filter, sort, and pagination
- User statistics (total, watched, average)
- Admin panel to manage the catalog
- Automated tests with CI/CD

## What is out of scope

- Movie recommendations (planned for Phase 4)
- Social features (comments, sharing)
- Multiple watch sessions per movie
- Streaming integration
- Mobile app

## Tech stack

Backend: Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16
Frontend: Vue 3, Vite, Vue Router, Axios
DevOps: Docker, GitHub Actions, Render
Testing: Pytest

## Live URLs

- Frontend: https://movie-watch-list-api.onrender.com
- Backend: https://movies.vorthe.ir
- API docs: https://movies.vorthe.ir/docs
