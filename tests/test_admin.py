from fastapi import status


def test_admin_read_all(client, test_movie):
    response = client.get("/admin/movie")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Brave Heart"


def test_admin_delete_movie(client, test_movie):
    response = client.delete(f"/admin/movie/{test_movie.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_admin_delete_movie_not_found(client):
    response = client.delete("/admin/movie/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Movie Not Found"}
