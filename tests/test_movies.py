from fastapi import status

MOVIE_PAYLOAD = {
    "title": "Test Movie",
    "description": "A test movie description",
    "rating": 5,
    "watched": False,
    "genre": "Action",
}


def test_read_all_authenticated(client, test_movie):
    response = client.get("/movies/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Brave Heart"


def test_read_one_authenticated(client, test_movie):
    response = client.get(f"/movies/movie/{test_movie.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Brave Heart"


def test_read_one_authenticated_not_found(client):
    response = client.get("/movies/movie/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Movie Not Found"}


def test_create_movie(client):
    response = client.post("/movies/movie", json=MOVIE_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED


def test_update_movie(client, test_movie):
    updated = {
        "title": "Updated Title",
        "description": "Updated description",
        "rating": 9,
        "watched": True,
        "genre": "Drama",
    }
    response = client.put(f"/movies/movie/{test_movie.id}", json=updated)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_movie_not_found(client):
    updated = {
        "title": "Updated Title",
        "description": "Updated description",
        "rating": 9,
        "watched": True,
        "genre": "Drama",
    }
    response = client.put("/movies/movie/999", json=updated)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_movie(client, test_movie):
    response = client.delete(f"/movies/movie/{test_movie.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_movie_not_found(client):
    response = client.delete("/movies/movie/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_stats(client, test_movie):
    response = client.get("/movies/stats")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_movies"] == 1
    assert data["watched_movies"] == 0
    assert data["unwatched_movies"] == 1
