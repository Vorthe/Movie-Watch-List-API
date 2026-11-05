from fastapi import status

MOVIE_PAYLOAD = {
    "title": "New Movie",
    "description": "New Description",
    "genre": "Action",
    "external_rating": 7.5,
    "external_id": "99999",
    "external_source": "tmdb",
}


def test_admin_list_catalog(client, test_movie):
    response = client.get("/admin/movies")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Brave Heart"


def test_admin_create_movie(client):
    response = client.post("/admin/movies", json=MOVIE_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Movie"
    assert data["external_rating"] == 7.5


def test_admin_create_duplicate_external(client):
    client.post("/admin/movies", json=MOVIE_PAYLOAD)
    response = client.post("/admin/movies", json=MOVIE_PAYLOAD)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_admin_update_movie(client, test_movie):
    updated = {
        "title": "Updated Title",
        "description": "Updated Description",
        "genre": "Sci-Fi",
        "external_rating": 9.0,
        "external_id": "12345",
        "external_source": "tmdb",
    }
    response = client.put(f"/admin/movies/{test_movie.id}", json=updated)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Title"


def test_admin_update_not_found(client):
    response = client.put("/admin/movies/999", json=MOVIE_PAYLOAD)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_delete_movie(client, test_movie):
    response = client.delete(f"/admin/movies/{test_movie.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(f"/admin/movies")
    assert get_response.json() == []


def test_admin_delete_not_found(client):
    response = client.delete("/admin/movies/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Movie Not Found"}
