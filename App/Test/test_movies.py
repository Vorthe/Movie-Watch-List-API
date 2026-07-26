from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..routers.movies import get_db, get_current_user
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Movies, Users

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


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


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


def test_read_all_authenticated(test_movie):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "title": "Brave Heart",
            "description": "very very sensetive movie",
            "rating": 8,
            "watched": False,
            "genre": "Drama",
            "owner_id": 1,
            "id": 1,
        }
    ]


def test_read_one_authenticated(test_movie):
    response = client.get("/movie/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "Brave Heart",
        "description": "very very sensetive movie",
        "rating": 8,
        "watched": False,
        "genre": "Drama",
        "owner_id": 1,
        "id": 1,
    }


def test_read_one_authenticated_not_found():
    response = client.get("/movie/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie Not Found"}


def test_create_movie(test_movie):
    request_data = {
        "title": "New Movie",
        "description": "New Movie Description",
        "rating": 4,
        "watched": False,
        "genre": "action",
    }
    response = client.post("/movie", json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Movies).filter(Movies.id == 2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.rating == request_data.get("rating")
    assert model.watched == request_data.get("watched")
    assert model.genre == request_data.get("genre")


def test_update_movie(test_movie):
    request_data = {
        "title": "Change the title",
        "description": "Update Movie Description",
        "rating": 4,
        "watched": False,
        "genre": "action",
    }
    response = client.put("/movie/1", json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Movies).filter(Movies.id == 1).first()
    assert model.title == "Change the title"


def test_update_movie_not_found(test_movie):
    request_data = {
        "title": "Change the title",
        "description": "Update Movie Description",
        "rating": 4,
        "watched": False,
        "genre": "action",
    }
    response = client.put("/movie/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie Not Found"}


def test_delete_movie(test_movie):
    response = client.delete("/movie/1")
    assert response.status_code == 200
    db = TestingSessionLocal()
    model = db.query(Movies).filter(Movies.id == 1).first()
    assert model is None
    
    
    
    
def test_delete_movie_not_found():
    response = client.delete("/movie/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie Not Found"}