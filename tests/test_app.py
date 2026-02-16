from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    response = client.post("/activities/Basketball Team/signup?email=newstudent@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]

    # Verify added
    response2 = client.get("/activities")
    data = response2.json()
    assert "newstudent@example.com" in data["Basketball Team"]["participants"]


def test_signup_duplicate():
    # First signup
    client.post("/activities/Basketball Team/signup?email=duplicate@example.com")
    # Second attempt
    response = client.post("/activities/Basketball Team/signup?email=duplicate@example.com")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_invalid_activity():
    response = client.post("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_remove_success():
    # Signup first
    client.post("/activities/Soccer Club/signup?email=removeme@example.com")
    # Then remove
    response = client.delete("/activities/Soccer Club/signup?email=removeme@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Removed" in result["message"]

    # Verify removed
    response2 = client.get("/activities")
    data = response2.json()
    assert "removeme@example.com" not in data["Soccer Club"]["participants"]


def test_remove_not_signed_up():
    response = client.delete("/activities/Soccer Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_remove_invalid_activity():
    response = client.delete("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # RedirectResponse