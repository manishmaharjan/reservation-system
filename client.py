import requests

class ReservationClient:
    def __init__(self, base_url):
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

