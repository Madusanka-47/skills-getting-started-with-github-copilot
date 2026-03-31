import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient
from src import app as app_module


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Debate Team" in data
    assert isinstance(data["Debate Team"]["participants"], list)
    assert data["Debate Team"]["max_participants"] == 16


def test_signup_creates_new_participant(client):
    activity = "Debate Team"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in app_module.activities[activity]["participants"]


def test_signup_duplicate_returns_bad_request(client):
    activity = "Debate Team"
    email = "alex@mergington.edu"

    response = client.post(
        f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity(client):
    activity = "Debate Team"
    email = "alex@mergington.edu"

    response = client.delete(
        f"/activities/{urllib.parse.quote(activity)}/participants/{urllib.parse.quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]


def test_remove_missing_participant_returns_not_found(client):
    activity = "Debate Team"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{urllib.parse.quote(activity)}/participants/{urllib.parse.quote(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
