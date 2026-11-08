import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from App.database import Base
from App.main import app
from App.models import Movie, UserMovieStatus, Users
from App.routers.auth import get_db as auth_get_db, get_current_user
from App.routers.movies import get_db as movies_get_db
from App.routers.admin import get_db as admin_get_db
from App.routers.users import get_db as users_get_db

TEST_DB_URL = "sqlite:///./testdb.db"


# Remove stale SQLite DB so schema is always rebuilt from current models
_TEST_DB_PATH = "./testdb.db"
if os.path.exists(_TEST_DB_PATH):
    os.remove(_TEST_DB_PATH)


engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "testuser", "id": 1, "user_role": "admin"}


app.dependency_overrides[auth_get_db] = override_get_db
app.dependency_overrides[movies_get_db] = override_get_db
app.dependency_overrides[admin_get_db] = override_get_db
app.dependency_overrides[users_get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_db():
    def _clean():
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM user_movie_status;"))
            conn.execute(text("DELETE FROM movies;"))
            conn.execute(text("DELETE FROM users;"))
            try:
                conn.execute(
                    text(
                        "DELETE FROM sqlite_sequence WHERE name IN "
                        "('user_movie_status', 'movies', 'users');"
                    )
                )
            except Exception:
                pass
            conn.commit()

    _clean()
    yield
    _clean()


@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    password_bytes = "test1234".encode("utf-8")[:72]
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    user = Users(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=hashed_password,
        is_active=True,
        role="admin",
        phone_number="09121234567",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_movie():
    db = TestingSessionLocal()
    movie = Movie(
        title="Brave Heart",
        description="A very sensitive movie",
        genre="Drama",
        external_rating=8.5,
        external_id="12345",
        external_source="tmdb",
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)
    db.close()
    return movie


@pytest.fixture
def test_status(test_movie):
    db = TestingSessionLocal()
    status = UserMovieStatus(
        user_id=1,
        movie_id=test_movie.id,
        watched=True,
        rating=9,
    )
    db.add(status)
    db.commit()
    db.refresh(status)
    db.close()
    return status
