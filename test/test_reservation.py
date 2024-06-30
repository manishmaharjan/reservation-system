import json
from datetime import datetime, timedelta
from test.test_config import client
from unittest.mock import patch

import pytest
from flask import Response

from src import db
from src.models import Reservation, Room, User

from .utils import create_reservation, create_user, delete_reservation


def test_create_get_reservation(client):
    api_key, user_id = create_user(client)
    headers = {"Api_key": api_key}
    reservation_data = {
        "date": "2024-06-30",
        "start-time": "10:00",
        "end-time": "11:30",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/", json=reservation_data, headers=headers
    )
    assert response.status_code == 201
    assert response.text == "Reservation created successfully"
    reservation_id = response.headers.get("reservation_id")

    assert isinstance(int(reservation_id), int)

    response = client.get(
        f"/api/users/{user_id}/reservations/{reservation_id}/", headers=headers
    )
    resevations = json.loads(response.data)
    assert response.status_code == 200
    assert len(resevations) > 0

    response = client.get


def test_invalid_user_id(client):
    api_key, user_id = create_user(client)
    headers = {"Api_key": api_key}

    response = client.get(f"/api/users/-4/reservations/1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.get(f"/api/users/invalid/reservations/1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.put(f"/api/users/-4/reservations/1/", headers=headers, json={})
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.put(
        f"/api/users/invalid/reservations/1/", headers=headers, json={}
    )
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.delete(f"/api/users/-4/reservations/1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.delete(f"/api/users/invalid/reservations/1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_invalid_user_id_collection(client):
    api_key, user_id = create_user(client)
    headers = {"Api_key": api_key}

    response = client.get(f"/api/users/-4/reservations/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.get(f"/api/users/invalid/reservations/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_invalid_api_key(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)

    # Incorrect API key (randomly generated)
    headers = {"Api-key": "random_api_key"}
    reservation_data = {
        "date": "2024-06-30",
        "start-time": "10:00",
        "end-time": "11:30",
        "roomId": 1,
    }

    # Attempt to create a reservation with incorrect API key
    response = client.post(
        f"/api/users/{user_id}/reservations/", json=reservation_data, headers=headers
    )
    assert response.status_code == 401
    assert response.text == "Incorrect api key."


def test_missing_api_key(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)

    # Omitting API key from headers
    reservation_data = {
        "date": "2024-06-30",
        "start-time": "10:00",
        "end-time": "11:30",
        "roomId": 1,
    }

    # Attempt to create a reservation without API key
    response = client.post(f"/api/users/{user_id}/reservations/", json=reservation_data)
    assert response.status_code == 401
    assert response.text == "Incorrect api key."


def test_api_key_id_not_matching_normal(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)
    user_data = {"username": "test_user1", "email": "test_user1@example.com"}
    api_key1, user_id1 = create_user(client, user_data)
    # Valid API key
    headers = {"api-key": api_key1}

    response = client.get(f"/api/users/{user_id}/reservations/1/", headers=headers)
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )

    response = client.put(
        f"/api/users/{user_id}/reservations/1/", headers=headers, json={}
    )
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )

    response = client.delete(f"/api/users/{user_id}/reservations/1/", headers=headers)
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )


def test_api_key_id_not_matching_collection(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)
    user_data = {"username": "test_user1", "email": "test_user1@example.com"}
    api_key1, user_id1 = create_user(client, user_data)
    # Valid API key
    headers = {"Api-key": api_key1}

    response = client.get(f"/api/users/{user_id}/reservations/", headers=headers)
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )

    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json={}
    )
    assert response.status_code == 401
    assert (
        response.text
        == "The provided Api-key does not correspond to the user_id provided."
    )


def test_update_reservation_success(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    # Create a reservation to update
    reservation_id = create_reservation(client, api_key, user_id)
    # Updated reservation data
    updated_reservation_data = {
        "date": "2024-07-01",
        "start-time": "15:00",
        "end-time": "16:30",
        "roomId": 2,
    }

    # Make PUT request to update reservation
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        json=updated_reservation_data,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.text == "Reservation updated successfully"


def test_update_reservation_invalid_user_id(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    # Create a reservation to update
    reservation_id = create_reservation(client, api_key, user_id)

    # Attempt to update reservation with invalid user ID in path
    response = client.put(
        f"/api/users/-4/reservations/{reservation_id}/", json={}, headers=headers
    )
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_update_reservation_invalid_room_id(client):
    # Create a user and get valid API key and user ID
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    # Create a reservation to update
    reservation_id = create_reservation(client, api_key, user_id)

    # Attempt to update reservation with invalid room ID
    invalid_room_data = {"roomId": 999}  # Non-existent room ID
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        json=invalid_room_data,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.text == "No room found with the provided room id."


def test_get_update_delete_unbelonging_reservation(client):
    api_key, user_id = create_user(client)

    user_data = {"username": "test_user1", "email": "test_user1@example.com"}
    api_key1, user_id1 = create_user(client, user_data)

    headers = {"Api-key": api_key1}

    reservation_id = create_reservation(client, api_key, user_id)
    response = client.get(
        f"/api/users/{user_id1}/reservations/{reservation_id}/", headers=headers
    )
    assert response.status_code == 403
    assert response.text == "Reservation does not belong to the provided user_id."

    response = client.put(
        f"/api/users/{user_id1}/reservations/{reservation_id}/",
        headers=headers,
        json={},
    )
    assert response.status_code == 403
    assert response.text == "Reservation does not belong to the provided user_id."

    response = client.delete(
        f"/api/users/{user_id1}/reservations/{reservation_id}/",
        headers=headers,
        json={},
    )
    assert response.status_code == 403
    assert response.text == "Reservation does not belong to the provided user_id."


def test_get_update_delete_no_existing_reservation(client):
    api_key, user_id = create_user(client)

    headers = {"Api-key": api_key}

    response = client.get(f"/api/users/{user_id}/reservations/9999/", headers=headers)
    assert response.status_code == 404
    assert response.text == "No reservation found with the provided reservation_id."

    response = client.put(
        f"/api/users/{user_id}/reservations/9999/", headers=headers, json={}
    )
    assert response.status_code == 404
    assert response.text == "No reservation found with the provided reservation_id."

    response = client.delete(
        f"/api/users/{user_id}/reservations/9999/", headers=headers
    )
    assert response.status_code == 404
    assert response.text == "No reservation found with the provided reservation_id."


def test_delete_reservation(client):
    api_key, user_id = create_user(client)

    headers = {"Api-key": api_key}

    reservation_id = create_reservation(client, api_key, user_id)
    response = client.delete(
        f"/api/users/{user_id}/reservations/{reservation_id}/", headers=headers
    )
    assert response.status_code == 200


def test_invalid_reservation_id(client):
    api_key, user_id = create_user(client)
    headers = {"Api_key": api_key}

    response = client.get(f"/api/users/{user_id}/reservations/-1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid reservation_id parameter"

    response = client.get(
        f"/api/users/{user_id}/reservations/invalid/", headers=headers
    )
    assert response.status_code == 400
    assert response.text == "Invalid reservation_id parameter"

    response = client.put(f"/api/users/{user_id}/reservations/-1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid reservation_id parameter"

    response = client.put(
        f"/api/users/{user_id}/reservations/invalid/", headers=headers
    )
    assert response.status_code == 400
    assert response.text == "Invalid reservation_id parameter"

    response = client.delete(f"/api/users/{user_id}/reservations/-1/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid reservation_id parameter"

    response = client.delete(
        f"/api/users/{user_id}/reservations/invalid/", headers=headers
    )
    assert response.status_code == 400
    assert response.text == "Invalid reservation_id parameter"


def test_invalid_reservation_id_collection(client):
    api_key, user_id = create_user(client)
    headers = {"Api_key": api_key}

    response = client.get(f"/api/users/-4/reservations/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.get(f"/api/users/invalid/reservations/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_put_not_json_format(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    reservation_id = create_reservation(client, api_key, user_id)

    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        data="torve",
    )
    assert response.status_code == 415
    assert response.text == "Request must be in JSON format."


def test_put_error_parsing_data(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    reservation_id = create_reservation(client, api_key, user_id)

    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json="torve",
    )
    assert response.status_code == 400
    assert response.text == "Error parsing JSON data"


def test_post_error_parsing_data(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json="torve"
    )
    assert response.status_code == 400
    assert response.text == "Error parsing JSON data"


def test_put_at_least_one_field(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    reservation_id = create_reservation(client, api_key, user_id)
    data = {}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 400
    assert (
        response.text
        == "At least one of date, start-time, end-time, or roomId is required."
    )


def test_put_invalid_time_or_date(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    reservation_id = create_reservation(client, api_key, user_id)

    data = {"start-time": "13-12"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )

    data = {"end-time": "manex"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )

    data = {"date": "2003-22-12", "end-time": "manex"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )

    data = {"date": "invalid", "end-time": "invalid"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )


def test_put_post_reservation_too_long(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    reservation_id = create_reservation(client, api_key, user_id)

    data = {"start-time": "13:00", "end-time": "19:00"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 409
    assert response.text == "Reservation is too long."


def test_put_time_slot_taken(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    reservation_id = create_reservation(
        client, api_key, user_id, start_time="11:00", end_time="12:00"
    )
    reservation_id1 = create_reservation(
        client, api_key, user_id, start_time="13:00", end_time="14:00"
    )
    data = {"start-time": "10:00", "end-time": "11:01"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id1}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 409
    assert response.text == "Time slot already taken"

    data = {"start-time": "10:59", "end-time": "12:01"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id1}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 409
    assert response.text == "Time slot already taken"

    data = {"start-time": "11:00", "end-time": "12:00"}
    response = client.put(
        f"/api/users/{user_id}/reservations/{reservation_id1}/",
        headers=headers,
        json=data,
    )

    assert response.status_code == 409
    assert response.text == "Time slot already taken"


def test_get_reservations(client):
    # Create a new user and get API key
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    # Test valid scenario
    response = client.get(f"/api/users/{user_id}/reservations/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Ensure response is a list of reservations

    # Test invalid user_id scenario
    response = client.get("/api/users/-4/reservations/", headers=headers)
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    # Test API key does not correspond to user_id scenario
    headers = {"Api-key": "invalidApikey"}
    response = client.get(f"/api/users/{user_id}/reservations/", headers=headers)
    assert response.status_code == 401
    assert response.text == "Incorrect api key."


def test_post_invalid_user_id(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}
    response = client.post("/api/users/-4/reservations/", headers=headers, data={})
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"

    response = client.post("/api/users/invalid/reservations/", headers=headers, data={})
    assert response.status_code == 400
    assert response.text == "Invalid user_id parameter"


def test_create_reservation(client):
    # Create a new user and get API key
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    # Test valid reservation creation
    reservation_data = {
        "date": "2024-06-30",
        "start-time": "10:00",
        "end-time": "11:30",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/", json=reservation_data, headers=headers
    )
    assert response.status_code == 201
    assert response.text == "Reservation created successfully"
    reservation_id = response.headers.get("reservation_id")
    assert isinstance(int(reservation_id), int)

    # Test missing/invalid reservation details scenario
    invalid_reservation_data = {"start-time": "10:00", "end-time": "11:30"}
    response = client.post(
        f"/api/users/{user_id}/reservations/",
        json=invalid_reservation_data,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.text == "date, start-time, end-time and roomId are required"

    # Test no room found with the provided room id scenario
    invalid_room_reservation_data = {
        "date": "2024-06-30",
        "start-time": "10:00",
        "end-time": "11:30",
        "roomId": 999,  # Assuming this room ID does not exist
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/",
        json=invalid_room_reservation_data,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.text == "No room found with the provided room id."

    # Test past time slot scenario
    past_time_reservation_data = {
        "date": "2020-06-30",  # Past date
        "start-time": "10:00",
        "end-time": "11:30",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/",
        json=past_time_reservation_data,
        headers=headers,
    )
    assert response.status_code == 409
    assert response.text == "Can not book past time slots"

    # Test reservation conflict scenario
    conflicting_reservation_data = {
        "date": "2024-06-30",
        "start-time": "10:30",
        "end-time": "11:30",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/",
        json=conflicting_reservation_data,
        headers=headers,
    )
    assert response.status_code == 409
    assert response.text == "Time slot already taken"

    # Test JSON format error scenario
    headers["Content-Type"] = "application/xml"  # Simulate incorrect content type
    response = client.post(
        f"/api/users/{user_id}/reservations/", json=reservation_data, headers=headers
    )
    assert response.status_code == 415
    assert response.text == "Request must be in JSON format."

    del headers["Content-Type"]  # Remove for subsequent tests


def test_post_invalid_time_or_date(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    data = {
        "date": "2024-06-30",
        "start-time": "11:00",
        "end-time": "akdm",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json=data
    )

    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )

    data = {
        "date": "2024:0:1321",
        "start-time": "11:00",
        "end-time": "12:00",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json=data
    )
    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )

    data = {"date": "2024-06-30", "start-time": "p", "end-time": "22222", "roomId": 1}
    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json=data
    )
    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )
    data = {
        "date": "invalid",
        "start-time": "11:00",
        "end-time": "invalid",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json=data
    )
    assert response.status_code == 400
    assert (
        response.text
        == "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM"
    )


def test_post_time_slot_too_long(client):
    api_key, user_id = create_user(client)
    headers = {"Api-key": api_key}

    data = {
        "date": "2024-06-30",
        "start-time": "11:00",
        "end-time": "15:00",
        "roomId": 1,
    }
    response = client.post(
        f"/api/users/{user_id}/reservations/", headers=headers, json=data
    )
    assert response.status_code == 409
    assert response.text == "Reservation is too long."
