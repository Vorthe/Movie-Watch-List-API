from fastapi import status

SIGNUP_PAYLOAD = {
    "username": "newuser",
    "email": "new@example.com",
    "first_name": "New",
    "last_name": "User",
    "password": "newpass1234",
    "role": "user",
    "phone_number": "09121234567",
}


def test_signup_success(client):
    response = client.post("/auth/", json=SIGNUP_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED


def test_signup_missing_required_fields(client):
    response = client.post("/auth/", json={"username": "x"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_short_phone_number(client):
    payload = {**SIGNUP_PAYLOAD, "phone_number": "123"}
    response = client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup_too_long_phone_number(client):
    payload = {**SIGNUP_PAYLOAD, "phone_number": "123456789012345"}
    response = client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
