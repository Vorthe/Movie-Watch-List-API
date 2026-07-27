from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Movies, Users
from ..routers.auth import bycrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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
    return {"username": "nim4044", "id": 1, "user_role": "admin"}


client = TestClient(app)


@pytest.fixture
def test_movie():
    movie = Movies(
        title="Brave Heart",
        description="very very sensetive movie",
        rating=8,
        watched=False,
        genre="Drama",
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(movie)
    db.commit()
    yield movie
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM movies;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        email="nim4044@gmail.com",
        username="nim4044",
        first_name="nima",
        last_name="salimi",
        hashed_password=bycrypt_context.hash("test1234"),
        is_active=1,
        role="admin",
        phone_number="09147249719",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
