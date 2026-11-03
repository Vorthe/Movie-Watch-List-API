import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from App.database import Base
from App.main import app
from App.models import Movies, Users
from App.routers.auth import bycrypt_context

# Import each router's get_db separately — they are distinct functions
from App.routers.auth import get_db as auth_get_db, get_current_user
from App.routers.movies import get_db as movies_get_db
from App.routers.admin import get_db as admin_get_db
from App.routers.users import get_db as users_get_db

TEST_DB_URL = "sqlite:///./testdb.db"

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


# Register overrides once for all routers
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
    """Raw DB session for tests that need direct access."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_db():
    """Clean tables before and after each test."""

    def _clean():
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM movies;"))
            conn.execute(text("DELETE FROM users;"))
            try:
                conn.execute(
                    text(
                        "DELETE FROM sqlite_sequence WHERE name IN ('movies', 'users');"
                    )
                )
            except Exception:
                pass  # sqlite_sequence may not exist
            conn.commit()

    _clean()
    yield
    _clean()


@pytest.fixture
def test_movie():
    db = TestingSessionLocal()
    movie = Movies(
        title="Brave Heart",
        description="very very sensetive movie",
        rating=8,
        watched=False,
        genre="Drama",
        owner_id=1,
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)
    db.close()
    return movie


@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    user = Users(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=bycrypt_context.hash("test1234"),
        is_active=1,
        role="admin",
        phone_number="09121234567",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user
