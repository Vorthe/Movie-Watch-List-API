from fastapi import status


def test_list_notifications_empty(client):
    response = client.get("/notifications/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_notifications_with_data(client, test_notification):
    response = client.get("/notifications/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Test notification"
    assert data[0]["read"] is False


def test_unread_count(client, test_notification):
    response = client.get("/notifications/unread-count")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"unread_count": 1}


def test_mark_read(client, test_notification):
    response = client.patch(f"/notifications/{test_notification.id}/read")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get("/notifications/unread-count")
    assert response.json() == {"unread_count": 0}


def test_mark_read_not_found(client):
    response = client.patch("/notifications/999/read")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_mark_all_read(client, test_notification):
    response = client.post("/notifications/read-all")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get("/notifications/unread-count")
    assert response.json() == {"unread_count": 0}


def test_signup_creates_welcome_notification(client):
    """Signup should enqueue welcome task; in eager mode, it runs immediately."""
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "newpass1234",
        "role": "user",
        "phone_number": "09121112222",
    }
    response = client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # Check notifications exist (since Celery is eager, task ran immediately)
    notif_response = client.get("/notifications/")
    # But we're overriding get_current_user as user_id=1, not the new user
    # So we need to query the DB directly
    from tests.conftest import TestingSessionLocal
    from App.models import Notification, Users

    db = TestingSessionLocal()
    try:
        user = db.query(Users).filter(Users.username == "newuser").first()
        assert user is not None

        notifications = (
            db.query(Notification).filter(Notification.user_id == user.id).all()
        )
        assert len(notifications) == 1
        assert "Welcome" in notifications[0].message
    finally:
        db.close()
