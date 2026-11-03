from fastapi import status


def test_login_success(client, test_user):
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "test1234"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "wrongpass"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/token",
        data={"username": "ghost", "password": "any"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
