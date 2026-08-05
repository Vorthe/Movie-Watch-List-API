from .utils import *
from ..App.routers.admin import get_current_user, get_db
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authentication(test_movie):
    response = client.get("/admin/movie")
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


def test_admin_delete_movie(test_movie):
    response = client.delete("/admin/movie/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Movies).filter(Movies.id == 1).first()
    assert model is None


def test_admin_delete_movie_not_found():
    response = client.delete("/admin/movie/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Movie Not Found"}
