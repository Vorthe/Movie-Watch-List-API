from fastapi import status

SIGNUP_PAYLOAD = {
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "newpass1234",
}


def test_signup_success(client):
    response = client.post("/auth/", json=SIGNUP_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED


def test_signup_missing_required_fields(client):
    response = client.post("/auth/", json={"email": "x@x.com"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_signup_short_password(client):
    payload = {**SIGNUP_PAYLOAD, "password": "12345"}
    response = client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_signup_ignores_role_from_client(client):
    payload = {**SIGNUP_PAYLOAD, "role": "admin"}
    response = client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    from App.models import Users
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    try:
        user = db.query(Users).filter(Users.email == "newuser@example.com").first()
        assert user is not None
        assert user.role == "user"
        assert user.username == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
    finally:
        db.close()
