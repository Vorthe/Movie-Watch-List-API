from datetime import date

from fastapi import status


def _today():
    return date.today().isoformat()


def test_create_schedule(client, test_movie):
    response = client.post(
        "/schedule/",
        json={"movie_id": test_movie.id, "scheduled_date": _today()},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["movie_id"] == test_movie.id
    assert data["status"] == "pending"
    assert data["completed_at"] is None
    assert data["movie"]["title"] == "Brave Heart"


def test_create_schedule_movie_not_found(client):
    response = client.post(
        "/schedule/",
        json={"movie_id": 999, "scheduled_date": _today()},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_schedule_duplicate(client, test_movie):
    payload = {"movie_id": test_movie.id, "scheduled_date": _today()}
    client.post("/schedule/", json=payload)
    response = client.post("/schedule/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_schedules(client, test_movie):
    client.post(
        "/schedule/",
        json={"movie_id": test_movie.id, "scheduled_date": _today()},
    )
    response = client.get("/schedule/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["movie_id"] == test_movie.id


def test_filter_schedules_by_status(client, test_movie):
    created = client.post(
        "/schedule/",
        json={"movie_id": test_movie.id, "scheduled_date": _today()},
    ).json()
    client.patch(f"/schedule/{created['id']}", json={"status": "done"})

    response = client.get("/schedule/?status=pending")
    assert response.json() == []

    response = client.get("/schedule/?status=done")
    assert len(response.json()) == 1


def test_update_schedule_to_done(client, test_movie):
    created = client.post(
        "/schedule/",
        json={"movie_id": test_movie.id, "scheduled_date": _today()},
    ).json()

    response = client.patch(f"/schedule/{created['id']}", json={"status": "done"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "done"
    assert data["completed_at"] is not None


def test_update_schedule_not_found(client):
    response = client.patch("/schedule/999", json={"status": "done"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_schedule(client, test_movie):
    created = client.post(
        "/schedule/",
        json={"movie_id": test_movie.id, "scheduled_date": _today()},
    ).json()

    response = client.delete(f"/schedule/{created['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get("/schedule/")
    assert response.json() == []


def test_delete_schedule_not_found(client):
    response = client.delete("/schedule/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_check_todays_schedules_task(client, test_movie):
    """Task should create a notification for today's pending schedule."""
    client.post(
        "/schedule/",
        json={"movie_id": test_movie.id, "scheduled_date": _today()},
    )

    from App.tasks import check_todays_schedules

    result = check_todays_schedules()
    assert result == {"checked": 1, "notifications_created": 1}

    notifs = client.get("/notifications/").json()
    assert len(notifs) == 1
    assert "Today's movie" in notifs[0]["message"]


def test_check_todays_schedules_task_no_schedules(client):
    """Task should return zeros when no schedules exist for today."""
    from App.tasks import check_todays_schedules

    result = check_todays_schedules()
    assert result == {"checked": 0, "notifications_created": 0}
