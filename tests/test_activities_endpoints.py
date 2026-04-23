"""
Tests for Mergington High School Activities API

These tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


# =============================================================================
# GET /activities Endpoint Tests
# =============================================================================


def test_get_activities_returns_all_activities(client):
    """
    Test that GET /activities returns all available activities.
    
    AAA Pattern:
    - Arrange: No explicit setup needed (fixtures handle it)
    - Act: Make GET request to /activities
    - Assert: Verify response status and that all activities are present
    """
    # Arrange
    expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(activity in data for activity in expected_activities)


def test_get_activities_includes_activity_details(client):
    """
    Test that each activity in the response contains required fields.
    
    AAA Pattern:
    - Arrange: Define expected structure
    - Act: Make GET request and inspect one activity
    - Assert: Verify all required fields are present
    """
    # Arrange
    required_fields = ["description", "schedule", "max_participants", "participants"]

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    chess_club = data["Chess Club"]
    assert all(field in chess_club for field in required_fields)
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert len(chess_club["participants"]) == 2


# =============================================================================
# POST /activities/{activity_name}/signup Endpoint Tests
# =============================================================================


def test_signup_for_activity_success(client):
    """
    Test successful signup for an activity.
    
    AAA Pattern:
    - Arrange: Prepare a new student email
    - Act: Make POST request to signup endpoint
    - Assert: Verify response status and confirmation message
    """
    # Arrange
    activity_name = "Chess Club"
    new_student = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_student}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert new_student in data["message"]
    assert activity_name in data["message"]


def test_signup_adds_participant_to_activity(client):
    """
    Test that signup actually adds the participant to the activity's participants list.
    
    AAA Pattern:
    - Arrange: Prepare student email and get initial count
    - Act: Sign up the student and fetch activities
    - Assert: Verify participant was added
    """
    # Arrange
    activity_name = "Chess Club"
    new_student = "newstudent@mergington.edu"
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Chess Club"]["participants"])

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_student}
    )
    final_response = client.get("/activities")
    final_count = len(final_response.json()["Chess Club"]["participants"])

    # Assert
    assert signup_response.status_code == 200
    assert final_count == initial_count + 1
    assert new_student in final_response.json()["Chess Club"]["participants"]


def test_signup_duplicate_student_returns_400(client):
    """
    Test that attempting to signup the same student twice returns a 400 error.
    
    AAA Pattern:
    - Arrange: Choose an already-signed-up student
    - Act: Attempt to signup the same student again
    - Assert: Verify 400 error is returned
    """
    # Arrange
    activity_name = "Chess Club"
    existing_student = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_student}
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_for_nonexistent_activity_returns_404(client):
    """
    Test that signup for a non-existent activity returns a 404 error.
    
    AAA Pattern:
    - Arrange: Prepare invalid activity name
    - Act: Attempt to signup for non-existent activity
    - Assert: Verify 404 error is returned
    """
    # Arrange
    invalid_activity = "Nonexistent Club"
    student_email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": student_email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


# =============================================================================
# DELETE /activities/{activity_name}/participants/{email} Endpoint Tests
# =============================================================================


def test_remove_participant_success(client):
    """
    Test successful removal of a participant from an activity.
    
    AAA Pattern:
    - Arrange: Choose an existing participant
    - Act: Make DELETE request to remove participant
    - Assert: Verify response status and confirmation message
    """
    # Arrange
    activity_name = "Chess Club"
    participant_to_remove = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_to_remove}"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert participant_to_remove in data["message"]
    assert activity_name in data["message"]


def test_remove_participant_actually_removes_from_list(client):
    """
    Test that removing a participant actually deletes them from the participants list.
    
    AAA Pattern:
    - Arrange: Get initial participant count
    - Act: Remove a participant and fetch updated activity
    - Assert: Verify participant count decreased and participant is gone
    """
    # Arrange
    activity_name = "Chess Club"
    participant_to_remove = "michael@mergington.edu"
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()["Chess Club"]["participants"])

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{participant_to_remove}"
    )
    final_response = client.get("/activities")
    final_count = len(final_response.json()["Chess Club"]["participants"])

    # Assert
    assert delete_response.status_code == 200
    assert final_count == initial_count - 1
    assert participant_to_remove not in final_response.json()["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    """
    Test that attempting to remove a non-existent participant returns 404.
    
    AAA Pattern:
    - Arrange: Choose an activity and a participant not in that activity
    - Act: Attempt to remove the participant
    - Assert: Verify 404 error is returned
    """
    # Arrange
    activity_name = "Chess Club"
    nonexistent_participant = "nonexistent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{nonexistent_participant}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_remove_from_nonexistent_activity_returns_404(client):
    """
    Test that attempting to remove from a non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Prepare invalid activity name
    - Act: Attempt to remove participant from non-existent activity
    - Assert: Verify 404 error is returned
    """
    # Arrange
    invalid_activity = "Nonexistent Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{invalid_activity}/participants/{participant_email}"
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


# =============================================================================
# Integration Tests
# =============================================================================


def test_signup_then_remove_flow(client):
    """
    Test complete flow: signup a new student, verify they appear, then remove them.
    
    AAA Pattern:
    - Arrange: Prepare test data
    - Act: Signup, verify, remove
    - Assert: Verify each step worked correctly
    """
    # Arrange
    activity_name = "Programming Class"
    new_student = "integration@mergington.edu"

    # Act & Assert - Signup
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_student}
    )
    assert signup_response.status_code == 200

    # Act & Assert - Verify added
    get_response = client.get("/activities")
    assert new_student in get_response.json()[activity_name]["participants"]

    # Act & Assert - Remove
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{new_student}"
    )
    assert delete_response.status_code == 200

    # Act & Assert - Verify removed
    final_response = client.get("/activities")
    assert new_student not in final_response.json()[activity_name]["participants"]
