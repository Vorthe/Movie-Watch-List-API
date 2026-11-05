from fastapi import status


def test_list_movies_empty(client):
    response = client.get("/movies/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_movies_with_catalog(client, test_movie):
    response = client.get("/movies/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Brave Heart"
    assert data[0]["external_rating"] == 8.5
    assert data[0]["user_status"] is None


def test_list_movies_with_status(client, test_movie, test_status):
    response = client.get("/movies/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["user_status"] == {"watched": True, "rating": 9}


def test_get_movie(client, test_movie):
    response = client.get(f"/movies/{test_movie.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Brave Heart"


def test_get_movie_not_found(client):
    response = client.get("/movies/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Movie Not Found"}


def test_put_status_creates_row(client, test_movie):
    response = client.put(
        f"/movies/{test_movie.id}/status",
        json={"watched": True, "rating": 8},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(f"/movies/{test_movie.id}")
    assert get_response.json()["user_status"] == {
        "watched": True,
        "rating": 8,
    }


def test_put_status_updates_existing(client, test_movie, test_status):
    response = client.put(
        f"/movies/{test_movie.id}/status",
        json={"watched": False, "rating": 5},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(f"/movies/{test_movie.id}")
    assert get_response.json()["user_status"] == {
        "watched": False,
        "rating": 5,
    }


def test_put_status_invalid_rating(client, test_movie):
    response = client.put(
        f"/movies/{test_movie.id}/status",
        json={"watched": True, "rating": 11},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_put_status_movie_not_found(client):
    response = client.put(
        "/movies/999/status",
        json={"watched": True, "rating": 5},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_status(client, test_movie, test_status):
    response = client.delete(f"/movies/{test_movie.id}/status")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(f"/movies/{test_movie.id}")
    assert get_response.json()["user_status"] is None


def test_delete_status_idempotent(client, test_movie):
    response = client.delete(f"/movies/{test_movie.id}/status")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_stats(client, test_movie, test_status):
    response = client.get("/movies/stats")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_movies"] == 1
    assert data["watched_movies"] == 1
    assert data["unwatched_movies"] == 0
    assert data["average_rating"] == 9


def test_search_movies(client, test_movie):
    response = client.get("/movies/?search=Brave")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    response = client.get("/movies/?search=Nonexistent")
    assert response.json() == []


def test_filter_watched(client, test_movie, test_status):
    response = client.get("/movies/?watched=true")
    assert len(response.json()) == 1

    response = client.get("/movies/?watched=false")
    assert response.json() == []
