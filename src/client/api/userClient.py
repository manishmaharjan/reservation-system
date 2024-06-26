import requests

API_URL = 'http://localhost:5000/api'

class UserClient:
    @staticmethod
    def create_user(username, email):
        response = requests.post(f'{API_URL}/users/', json={'username': username, 'email': email})
        if response.status_code == 201:
            api_key = response.headers.get('api_key')
            userId = response.headers.get('user_id')
            return {'user_id': userId,  'api_key': api_key }
        else:
            return f'{response.status_code} - {response.text}'

    @staticmethod
    def get_user(user_id, api_key):
        headers = {'Api-key': api_key}
        response = requests.get(f'{API_URL}/users/{user_id}/', headers=headers)
        return f'{response.status_code} - {response.text}'
    
    @staticmethod
    def update_user(user_id, api_key, username = None, email = None ):
        headers = {'Api-key': api_key}
        data = {}
        if username:
            data['username'] = username
        if email:
            data['email'] = email
        response = requests.put(f'{API_URL}/users/{user_id}/', json=data, headers= headers)
        return f'{response.status_code} - {response.text}'

    @staticmethod
    def delete_user(user_id, api_key):
        headers = {'Api-key': api_key}
        response = requests.delete(f'{API_URL}/users/{user_id}/', headers= headers)
        return f'{response.status_code} - {response.text}'
