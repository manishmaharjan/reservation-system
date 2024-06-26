import requests

API_URL = 'http://localhost:5000/api'

class AvailabilityClient:

    @staticmethod
    def get_available_rooms(date, time, duration=None):
        params = {
            'date': date,
            'time': time
        }
        if duration is not None:
            params['duration'] = duration

        response = requests.get(f'{API_URL}/rooms_available', params=params)
        return f'{response.status_code} - {response.text}'
        