from datetime import timedelta
import random

def create_user(client, user_data = {
        "username": "test_user",
        "email": "test_user@example.com"
    }):
    """Helper function to create a user."""
    response = client.post("/api/users/", json=user_data)
    return response.headers.get('api_key'), response.headers.get('user_id')
from datetime import datetime, timedelta

def create_reservation(client, api_key, user_id, date = "2024-06-30",  start_time = "10:00", end_time = "11:30", roomId = 1):

    reservation_data = {
        "date": date,
        "start-time": start_time,
        "end-time": end_time,
        "roomId": roomId
    }
    
    headers = {"Api-key": api_key}
    response = client.post(f"/api/users/{user_id}/reservations/", json=reservation_data, headers=headers)
    return response.headers.get("reservation_id")


def delete_reservation(client, api_key, user_id, reservation_id):
    """Helper function to delete a reservation."""
    headers = {"Api-key": api_key}
    response = client.delete(f"/api/reservations/{user_id}/{reservation_id}", headers=headers)
    return response
