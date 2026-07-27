from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "nim4044@gmail.com"
    assert response.json()["username"] == "nim4044"
    assert response.json()["first_name"] == "nima"
    assert response.json()["last_name"] == "salimi"
    assert response.json()["is_active"] == 1
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "09147249719"


def test_change_password_success(test_user):
    response = client.put(
        "/users/password",
        json={"password": "test1234", "new_password": "newpassword"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response = client.put(
        "/users/password",
        json={"password": "wrongpassword", "new_password": "password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error On Password Change"}
    
    
    
    
def test_change_phone_number_success(test_user):
    response=client.put("/users/phone_number/09147249720")
    assert response.status_code==status.HTTP_204_NO_CONTENT