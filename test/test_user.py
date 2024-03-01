import pytest
from unittest.mock import patch, MagicMock
from flask import Request, Flask
from src.models import ApiKey
from src.resources.user import RegisterUser

class TestRegisterUser:

    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def setup_method(self):
        # Set up initial configuration for tests
        self.register_user = RegisterUser()

    def teardown_method(self):
        # Clean up after each test
        pass

    def test_register_user_success(self, app, client):
        # Test registering a user with valid data
        with app.test_request_context('/'):
            with patch('src.resources.user.db.session.add'), \
                patch('src.resources.user.db.session.commit'), \
                patch.object(ApiKey, 'create_token', return_value='test_token'), \
                patch.object(Request, 'is_json', MagicMock(return_value=True)), \
                patch.object(Request, 'get_json', return_value={'username': 'testuser', 'email': 'test@example.com'}):

                response = self.register_user.post()
                assert response.status_code == 201  # User is created successfully
                assert response.headers.get('api_key') == 'test_token'  # API token is returned

    def test_register_user_username_exists(self, app, client):
        # Test registering a user with an existing username
        with app.test_request_context('/'):
            with patch('src.resources.user.db.session.add'), \
                patch('src.resources.user.db.session.rollback'), \
                patch.object(Request, 'is_json', MagicMock(return_value=True)), \
                patch.object(Request, 'get_json', return_value={'username': 'existing_user', 'email': 'test@example.com'}):
                
                response = self.register_user.post()
                assert response.status_code == 409  # Username already exists

    def test_register_user_invalid_email(self, app, client):
        # Test registering a user with an invalid email
        with app.test_request_context('/'):
            with patch.object(Request, 'is_json', MagicMock(return_value=True)), \
                patch.object(Request, 'get_json', return_value={'username': 'testuser', 'email': 'invalid_email'}):
                
                response = self.register_user.post()
                assert response.status_code == 409  # Incorrect email format
