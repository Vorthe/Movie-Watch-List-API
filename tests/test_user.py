from fastapi import status


def test_return_user(client, test_user):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["role"] == "admin"
    assert data["phone_number"] == "09121234567"


def test_change_password_success(client, test_user):
    response = client.put(
        "/users/password",
        json={"password": "test1234", "new_password": "newpass1234"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current(client, test_user):
    response = client.put(
        "/users/password",
        json={"password": "wrongpass", "new_password": "newpass1234"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error On Password Change"}


def test_change_phone_number_success(client, test_user):
    response = client.put("/users/phone_number/09129999999")
    assert response.status_code == status.HTTP_204_NO_CONTENT
