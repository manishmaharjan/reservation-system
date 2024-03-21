import pytest
import sys
sys.path.append("C:\\Users\\amael\\OneDrive\\Bureau\\reservation-system-main")
from unittest.mock import patch, MagicMock
from flask import Request, Flask
from flask_sqlalchemy import SQLAlchemy
from src import db
from src.models import ApiKey, User, db
from src.resources.user import RegisterUser


@pytest.fixture
def test_db():
    # Fixture for SQLAlchemy database
    # Place initialization code for your database here for tests
    # Make sure this function returns the correctly configured database object
    yield db

@pytest.fixture
def app():
    # Create an instance of your Flask application for testing
    app = Flask(__name__)
    
    # Configure SQLAlchemy only if it hasn't been initialized already
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
    
    return app



@pytest.fixture
def client(app):
    # Create a Flask test client to interact with the application in tests
    return app.test_client()

@pytest.fixture
def register_user():
    # Create an instance of RegisterUser for testing
    return RegisterUser()


def test_register_user_success(app, client, register_user):
    # Test registering a user with valid data
    with app.test_request_context('/'):
        with patch('src.models.ApiKey.create_token', return_value='test_token'), \
                patch('src.resources.user.db.session.add'), \
                patch('src.resources.user.db.session.commit'), \
                patch.object(Request, 'is_json', MagicMock(return_value=True)), \
                patch.object(Request, 'get_json', return_value={'username': 'testuser', 'email': 'test@example.com'}):

            response = register_user.post()
            assert response.status_code == 201  # User is created successfully
            assert response.headers.get('api_key') == 'test_token'  # API token is returned

def test_register_user_username_exists(app, client, register_user, test_db):
    with app.app_context():
        # Create an existing user in the database
        existing_user = User(username='existing_user', email='test@example.com')  
        test_db.session.add(existing_user)
        test_db.session.commit()

        # Check that the existing user has been correctly added to the database
        print(User.query.all())

        # Simulate a POST request with an existing username
        with app.test_request_context('/', method='POST', json={'username': 'existing_user', 'email': 'test@example.com'}):
            response = register_user.post()

        # Print the response received from the POST request
        print(response.data)

        # Check that the response status code is 409 (Conflict)
        assert response.status_code == 409


def test_register_user_invalid_json(app, client, register_user):
    with app.test_request_context('/', json={}):  # Passing an empty dictionary to simulate an invalid JSON request
        # Test registering a user with invalid JSON
        with patch.object(Request, 'is_json', MagicMock(return_value=False)):
            response = register_user.post()

            assert response.status_code == 400


def test_register_user_missing_data(app, client, register_user):
    with app.test_request_context('/'):
    # Test registering a user with missing data
        with patch.object(Request, 'is_json', MagicMock(return_value=True)), \
            patch.object(Request, 'get_json', return_value={}):
        
            response = register_user.post()

            assert response.status_code == 400

def test_register_user_invalid_email(app, client, register_user):
    # Test registering a user with an invalid email
    with app.test_request_context('/'):
        with patch.object(Request, 'is_json', MagicMock(return_value=True)), \
                patch.object(Request, 'get_json', return_value={'username': 'testuser', 'email': 'invalid_email'}):
            
            response = register_user.post()
            assert response.status_code == 409  # Incorrect email format

