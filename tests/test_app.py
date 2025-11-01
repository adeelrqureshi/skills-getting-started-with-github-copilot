import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]

def test_signup_for_activity():
    """Test signing up for an activity"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test that signing up twice fails"""
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already registered in this activity
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"  # Using an existing participant
    
    # Unregister the participant
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering when not registered"""
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()