import json
from test.test_config import client

import pytest

from src.models import ApiKey, User

from .utils import create_user


# Test case to create a user
def test_create_user(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201

    api_key = response.headers.get("api_key")
    user_id = response.headers.get("user_id")
    assert user_id is not None
    assert api_key is not None

    created_user = User.query.filter_by(username=user_data["username"]).first()
    assert created_user is not None
    assert created_user.email == user_data["email"]


# Test case to retrieve a user by ID
def test_get_user_by_id(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    headers = {"api_key": api_key}
    response = client.get(f"/api/users/{user_id}/", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


# Test case to update a user
def test_update_user(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    updated_user_data = {
        "username": "updated_user",
        "email": "updated_user@example.com",
    }
    headers = {"api_key": api_key}
    response = client.put(
        f"/api/users/{user_id}/", json=updated_user_data, headers=headers
    )
    assert response.status_code == 200

    updated_user = User.query.filter_by(id=user_id).first()
    assert updated_user is not None
    assert updated_user.username == updated_user_data["username"]
    assert updated_user.email == updated_user_data["email"]


# Test case to delete a user
def test_delete_user(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    headers = {"api_key": api_key}
    response = client.delete(f"/api/users/{user_id}/", headers=headers)
    assert response.status_code == 200
    deleted_user = User.query.filter_by(id=user_id).first()
    assert deleted_user is None


# Test case for trying to get a non-existent user with a fake api
def test_get_nonexistent_user_non_existent_api(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": "fake_api_key"}
    response = client.get("/api/users/99999/", headers=headers)
    assert response.status_code == 401


# Test case for trying to get a non-existent user
def test_get_nonexistent_user_existent_api(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.get("/api/users/99999/", headers=headers)
    assert response.status_code == 404


# Test case for trying to update a user with invalid data
def test_update_user_invalid_email(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    invalid_user_data = {"email": "invalid_email"}
    headers = {"api_key": api_key}
    response = client.put(
        f"/api/users/{user_id}/", json=invalid_user_data, headers=headers
    )
    assert response.status_code == 409
    assert response.text == "Incorrect email format"


def test_post_user_invalid_email(client):
    user_data = {"username": "test_user", "email": "invalid_email"}

    response = client.post(f"/api/users/", json=user_data)
    assert response.status_code == 409
    assert response.text == "Incorrect email format"


# Test case for trying to delete a user with an invalid API key
def test_delete_user_invalid_api_key(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    headers = {"api_key": "fake_api_key"}
    response = client.delete(f"/api/users/{user_id}/", headers=headers)
    assert response.status_code == 401


# Test case for trying to create a user with missing fields
def test_create_user_missing_fields(client):
    user_data = {
        "username": "test_user"
        # Missing email field
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 400
    assert response.text == "Username and email are required"


# Test creating a user with a duplicate username.
def test_create_user_duplicate_username(client):
    user_data = {"username": "duplicate_user", "email": "duplicate_user@example.com"}
    create_user(client, user_data)  # First creation should succeed
    response = client.post(
        "/api/users/", json=user_data
    )  # Second creation with same username should fail
    assert response.status_code == 409
    assert response.text == "Username already exists"


def test_try_get_all_users(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    response = client.get("/api/users/", headers=headers)
    assert response.status_code == 401
    assert response.data == b"The provided Api-key does not belong to an admin account"


def test_try_get_all_users_inexsitent_key(client):
    headers = {"Api-key-wrong": "invalid"}
    response = client.get("/api/users/", headers=headers)
    assert response.status_code == 401
    assert response.data == b"The provided Api-key does not belong to an admin account"


def test_get_all_users(client):
    """Test creating an admin user and then retrieving all users."""

    headers = {"api_key": "aa"}
    response = client.get("/api/users/", headers=headers)

    assert response.status_code == 200
    users = json.loads(response.data)

    assert len(users) >= 2  # At least the admin and one regular user


def test_get_all_users_normal_api_key(client):
    """Test creating an admin user and then retrieving all users."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.get("/api/users/", headers=headers)

    assert response.status_code == 401
    assert response.text == "The provided Api-key does not belong to an admin account"


def test_non_existent_user_id_get(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.get("/api/users/999999/", headers=headers)
    assert response.status_code == 404


def test_non_existent_user_id_put(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    updated_user_data = {
        "username": "updated_user",
        "email": "updated_user@example.com",
    }
    response = client.put("/api/users/999999/", json=updated_user_data, headers=headers)
    assert response.status_code == 404


def test_non_existent_user_id_delete(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.delete("/api/users/999999/", headers=headers)
    assert response.status_code == 404


def test_delete_user_missing_api_key(client):
    response = client.delete("/api/users/1/")
    assert response.status_code == 401


def test_get_invalid_user_id(client):
    """Test case for handling invalid user ID in GET request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.get("/api/users/manex/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_get_negative_user_id(client):
    """Test case for handling invalid user ID in GET request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.get("/api/users/-1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_update_invalid_user_id(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.put("/api/users/manex/", json=user_data, headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_update_negative_user_id(client):
    """Test case for handling invalid user ID in GET request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.put("/api/users/-1/", json=user_data, headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_delete_invalid_user_id(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.delete("/api/users/manex/", json=user_data, headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_delete_negative_user_id(client):
    """Test case for handling invalid user ID in GET request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.delete("/api/users/-1/", json=user_data, headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_get_user_not_found(client):
    """Test case for handling non-existent user in GET request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}
    response = client.get("/api/users/999999/", headers=headers)
    assert response.status_code == 404
    assert response.text == "User not found"


def test_put_update_user_conflict(client):
    """Test case for handling conflicting email in PUT request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    headers = {"api_key": api_key}

    updated_user_data = {"username": "admin"}  # Conflicting email
    response = client.put(
        f"/api/users/{user_id}/", json=updated_user_data, headers=headers
    )
    assert response.status_code == 409
    assert response.data == b"Username already exists"


def test_delete_user_not_authorized(client):
    """Test case for handling unauthorized DELETE request."""
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)
    user_data = {"username": "test_user1", "email": "test_user1@example.com"}
    api_key1, user_id1 = create_user(client, user_data)
    headers = {"api_key": api_key1}
    response = client.delete(f"/api/users/{user_id}/", headers=headers)
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )


def test_create_not_json(client):
    user_data = "manex"
    resp = client.post("/api/users/", data=user_data)
    assert resp.status_code == 415
    assert resp.text == "Request must be in JSON format."


def test_create_incorrect_json(client):
    user_data = "manex"
    resp = client.post("/api/users/", json=user_data)
    assert resp.status_code == 400
    assert resp.text == "Error parsing JSON data"


def test_get_correct_api_wrong_user(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    headers = {"api_key": api_key}
    response = client.get(f"/api/users/1/", headers=headers)
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )


def test_put_correct_api_wrong_user(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    headers = {"api_key": api_key}
    response = client.put(f"/api/users/1/", headers=headers, json=user_data)
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )


def test_no_username_no_email_provided(client):
    user_data = {"username": "test_user", "email": "test_user@example.com"}
    api_key, user_id = create_user(client, user_data)

    headers = {"api_key": api_key}
    new_data = {"field": "data"}
    response = client.put(f"/api/users/{user_id}/", headers=headers, json=new_data)

    assert response.status_code == 400
    assert response.text == "No username or email provided"
