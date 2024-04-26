"""Module providing function of time"""
import datetime
from json import JSONDecodeError
import requests

class ReservationClient:
    """Class used to reserve rooms by interacting with the API"""

    def __init__(self, base_url):
        """
        Initialize the ReservationClient with the base URL of the API.

        Args:
            base_url (str): The base URL of the API.
        """
        self.base_url = base_url

    def get_reservations(self):
        """
        Get a list of reservations from the API.

        Returns:
            dict: JSON response containing reservations data.
        """
        url = f"{self.base_url}/api/reservations/"
        response = requests.get(url)
        return response.json()

    def create_reservation(self, room_id, start_time, end_time, api_key):
        """
        Create a reservation for a room using the API.

        Args:
            room_id (int): The ID of the room to reserve.
            start_time (str): The start time of the reservation (in ISO format).
            end_time (str): The end time of the reservation (in ISO format).
            api_key (str): The API key for authentication.

        Returns:
            dict: JSON response containing reservation data.
        """
        url = f"{self.base_url}/api/reservations/{room_id}/"
        headers = {"Api-key": api_key}
        data = {"start_time": start_time, "end_time": end_time}
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def delete_reservation(self, room_id, reservation_id, api_key):
        """
        Delete a reservation using the API.

        Args:
            room_id (int): The ID of the room for which the reservation is made.
            reservation_id (int): The ID of the reservation to delete.
            api_key (str): The API key for authentication.

        Returns:
            dict: JSON response containing information about the deleted reservation.
        """
        url = f"{self.base_url}/api/reservations/{room_id}/{reservation_id}/"
        headers = {"Api-key": api_key}
        response = requests.delete(url, headers=headers)
        return response.json()

    def get_user_reservations(self, user_id, api_key):
        """
        Get reservations made by a specific user using the API.

        Args:
            user_id (int): The ID of the user.
            api_key (str): The API key for authentication.

        Returns:
            dict: JSON response containing reservations data for the user.
        """
        url = f"{self.base_url}/api/user/{user_id}/reservations/"
        headers = {"Api-key": api_key}
        response = requests.get(url, headers=headers)
        return response.json()

    def register_user(self, username, email):
        """
        Register a new user using the API.

        Args:
            username (str): The username of the new user.
            email (str): The email address of the new user.

        Returns:
            str: The API key generated for the new user.
        """
        url = f"{self.base_url}/api/user/register/"
        data = {"username": username, "email": email}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                return response.headers.get("api_key")
            else:
                return None
        except JSONDecodeError:
            return None

    def create_weekly_reservation(self, room_id, start_date, end_date, start_time, end_time, api_key):
        """
        Create weekly reservations for a room using the API.

        Args:
            room_id (int): The ID of the room to reserve.
            start_date (str): The start date of the weekly reservations (in ISO format).
            end_date (str): The end date of the weekly reservations (in ISO format).
            start_time (str): The start time of each reservation (in ISO format).
            end_time (str): The end time of each reservation (in ISO format).
            api_key (str): The API key for authentication.

        Returns:
            list: List of JSON responses containing reservation data for each created reservation.
        """
        # Convert start_date and end_date strings to datetime objects
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        # List to store JSON responses for each created reservation
        responses = []

        # Loop through each week between start_date and end_date
        current_date = start_date
        while current_date <= end_date:
            # Calculate start and end datetime objects for the current week
            week_start_datetime = datetime.datetime.combine(current_date, datetime.datetime.strptime(start_time, "%H:%M").time())
            week_end_datetime = datetime.datetime.combine(current_date, datetime.datetime.strptime(end_time, "%H:%M").time())

            # Create reservation for the current week
            response = self.create_reservation(room_id, week_start_datetime.isoformat(), week_end_datetime.isoformat(), api_key)
            responses.append(response)

            # Move to the next week
            current_date += datetime.timedelta(days=7)

        return responses
