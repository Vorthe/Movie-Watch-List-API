# Movie Watch List API

A Movie Watch List API built with FastAPI for learning and practicing modern backend development.

The project demonstrates:

* REST API development with FastAPI
* JWT Authentication
* PostgreSQL integration
* SQLAlchemy ORM
* Alembic database migrations
* Docker & Docker Compose
* Automatic database migrations on container startup

---

## Features

* JWT Authentication
* User Management
* Movie Watch List Management
* PostgreSQL Database
* SQLAlchemy ORM
* Alembic Migrations
* Dockerized Deployment

---

## Technologies

* Python 3.13
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Docker
* Docker Compose

---

## Project Structure

```text
movie-watch-list-api/
│
├── App/
│   ├── routers/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── ...
│
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

## Prerequisites

Make sure you have installed:

* Docker Desktop
* Git

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Vorthe/Movie-Watch-List-API.git
```

### 2. Move into the project

```bash
cd movie-watch-list-api
```

### 3. Create the environment file

Create a `.env` file based on `.env.example`.

Example:

```env
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

DATABASE_URL=postgresql://your_username:your_password@db:5432/your_database

SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

---

## Run the project

Build and start the containers:

```bash
docker compose up --build
```

The application automatically applies all Alembic migrations before starting the FastAPI server.

---

## API Documentation

Swagger UI:

```
http://localhost:8000/docs
```

---

## Stop the project

```bash
docker compose down
```

---

## Remove containers and database volume

```bash
docker compose down -v
```

---

## Notes

* PostgreSQL runs inside a Docker container.
* Database data is persisted using a Docker volume.
* Alembic migrations are automatically executed when the application container starts.
* Sensitive information is stored in `.env` and is **not** committed to Git.
* `.env.example` is provided as a template for local configuration.
