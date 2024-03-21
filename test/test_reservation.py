import pytest
import sys
sys.path.append("C:\\Users\\amael\\OneDrive\\Bureau\\reservation-system-main")
from flask import Flask, Response, request
from src import db
from src.models import Room, Reservation, User, db
from src.resources.reservation import CreateReservation, DeleteReservation, GetReservations
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


with app.app_context():
    user = User(username="test_user", email="test@example.com")
    db.session.add(user)
    db.session.commit()


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    # Create tables in the database
    with app.app_context():
        db.create_all()

    yield app

    # Remove tables from the database after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def create_reservation_resource():
    return CreateReservation()

@pytest.fixture
def delete_reservation_resource():
    return DeleteReservation()

@pytest.fixture
def get_reservations_resource():
    return GetReservations()

@pytest.fixture
def mock_request():
    return MagicMock()

@pytest.fixture
def mock_user():
    return User(username="admin", email="admin@example.com")

@pytest.fixture
def mock_room():
    return MagicMock()

@pytest.fixture
def mock_reservation():
    return MagicMock()

@pytest.fixture
def delete_reservation_instance():
    return DeleteReservation()

def test_create_reservation(app, client, create_reservation_resource, mock_user, mock_room):
    with app.test_request_context('/', method='POST', json={
        'date': '2024-03-01',
        'start_time': '10:00',
        'end_time': '11:00'
    }):
        # Mocking overlapping_reservations
        overlaping_reservations = []
        query_mock = MagicMock()
        query_mock.all.return_value = overlaping_reservations
        filter_mock = MagicMock(return_value=query_mock)
        Reservation.query.filter = filter_mock

        # Injecting the mock_user and mock_room instead of real objects
        response = create_reservation_resource.post(mock_user, mock_room)

        assert response.status_code == 209
        assert Reservation.query.count() == 1



def test_post_invalid_json(app, create_reservation_resource, mock_request):
    with app.test_request_context():
        mock_request.is_json = False
        response = create_reservation_resource.post(None, None)
        assert response.status == 415

def test_post_invalid_date_time_format(app, create_reservation_resource, mock_request):
    with app.test_request_context():
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'date': '2024-03-21',
            'start_time': '10:00:00',  # Invalid format
            'end_time': '12:00'
        }
        response = create_reservation_resource.post(None, None)
        assert response.status == 400

def test_post_past_time_slot(app, create_reservation_resource, mock_request):
    with app.test_request_context():
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'date': '2020-01-01',  # Past date
            'start_time': '10:00',
            'end_time': '12:00'
        }
        response = create_reservation_resource.post(None, None)
        assert response.status == 409

def test_post_reservation_too_long(app, create_reservation_resource, mock_request, mock_room):
    with app.test_request_context():
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'date': '2024-03-21',
            'start_time': '10:00',
            'end_time': '16:00'
        }
        mock_room.max_time = 300  # Assuming max_time is 5 hours (300 minutes)
        response = create_reservation_resource.post(None, mock_room)
        assert response.status == 409

def test_post_overlapping_reservations(app, create_reservation_resource, mock_request, mock_room, mock_user, mock_reservation):
    with app.test_request_context():
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'date': '2024-03-21',
            'start_time': '10:00',
            'end_time': '12:00'
        }
        mock_reservation.query.filter.return_value.all.return_value = [mock_reservation]  # Simulating overlapping reservation
        with patch('src.resources.reservation.db.session.add') as mock_add, \
             patch('src.resources.reservation.db.session.commit'):
            response = create_reservation_resource.post(mock_user, mock_room)
            mock_add.assert_not_called()  # Reservation shouldn't be added
            assert response.status == 409


def test_delete_reservation_success(delete_reservation_instance, mocker):
    # Create test data
    user = "test_user"
    room = "test_room"
    reservation_id = 1

    # Mock the query.filter_by method of Reservation class
    mocker.patch.object(Reservation, 'query')
    mocked_query = mocker.MagicMock()
    Reservation.query.filter_by.return_value = mocked_query
    mocked_query.first.return_value = Reservation(id=reservation_id, user=user, room=room)

    # Mock db.session.delete and db.session.commit
    mocker.patch.object(db.session, 'delete')
    mocker.patch.object(db.session, 'commit')

    # Call the delete method of DeleteReservation class
    response = delete_reservation_instance.delete(user, room, reservation_id)

    # Assertions
    assert response.status == 204
    db.session.delete.assert_called_once_with(Reservation(id=reservation_id, user=user, room=room))
    db.session.commit.assert_called_once()

def test_delete_reservation_not_found(delete_reservation_instance, mocker):
    # Create test data
    user = "test_user"
    room = "test_room"
    reservation_id = 9999

    # Mock the query.filter_by method of Reservation class
    mocker.patch.object(Reservation, 'query')
    mocked_query = mocker.MagicMock()
    Reservation.query.filter_by.return_value = mocked_query
    mocked_query.first.return_value = None

    # Call the delete method of DeleteReservation class
    response = delete_reservation_instance.delete(user, room, reservation_id)

    # Assertions
    assert response.status == 404

if __name__ == "__main__":
    pytest.main()
