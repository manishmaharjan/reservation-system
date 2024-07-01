import requests

API_URL = "http://localhost:5000/api"


class ReservationClient:

    @staticmethod
    def create_reservation(user_id, roomId, date, start_time, end_time, api_key):
        headers = {"Api-key": api_key}
        body = {
            "date": date,
            "start-time": start_time,
            "end-time": end_time,
            "roomId": roomId,
        }
        response = requests.post(
            f"{API_URL}/users/{user_id}/reservations/", json=body, headers=headers
        )
        return f"{response.status_code} - {response.text}"

    @staticmethod
    def get_reservations(user_id, api_key):
        headers = {"Api-key": api_key}
        response = requests.get(
            f"{API_URL}/users/{user_id}/reservations/", headers=headers
        )
        return f"{response.status_code} - {response.text}"

    @staticmethod
    def get_reservation(user_id, reservation_id, api_key):
        headers = {"Api-key": api_key}
        response = requests.get(
            f"{API_URL}/users/{user_id}/reservations/{reservation_id}/", headers=headers
        )
        return f"{response.status_code} - {response.text}"

    @staticmethod
    def put_reservation(
        user_id,
        reservation_id,
        api_key,
        date=None,
        start_time=None,
        end_time=None,
        room_id=None,
    ):
        headers = {"Api-key": api_key}
        data = {}
        if date:
            data["date"] = date
        if start_time:
            data["start-time"] = start_time
        if end_time:
            data["end-time"] = end_time
        if room_id:
            data["roomId"] = room_id

        response = requests.put(
            f"{API_URL}/users/{user_id}/reservations/{reservation_id}/",
            json=data, 
            headers=headers
        )
        return f"{response.status_code} - {response.text}"
        
    @staticmethod
    def delete_reservation(user_id, reservation_id, api_key):
        headers = {'Api-key': api_key}
        response = requests.delete(
            f"{API_URL}/users/{user_id}/reservations/{reservation_id}/", 
            headers=headers
        )
        return f'{response.status_code} - {response.text}'


      
