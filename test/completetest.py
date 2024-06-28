import sys
import unittest
from os import path

import self

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from unittest.mock import MagicMock, patch

from flask import Flask
from flask_restful import Api

from src import create_app
from src.models import Reservation, Room, User, db
from src.resources.reservation import ReservationId


class TestReservationId(unittest.TestCase):
    def setUp(self):
        self.app = create_app()  # create an instance of your Flask application
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()  # push an application context
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer mock_api_key'

    def tearDown(self):
        self.app_context.pop()  # pop the application context when done

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    def test_get_reservation_success(self, mock_query):
        # Mocking the Reservation object
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.user_id = 1
        mock_reservation.serialize.return_value = {"user": "john_doe", "room": "Conference Room 1", "date": "2023-05-28", "time-span": "10:00 - 11:00"}

        # Mocking the query filter
        mock_query.filter_by.return_value.first.return_value = mock_reservation

        # Mocking the User object
        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        response = reservation_id_resource.get(mock_user, 1, 1)

        self.assertEqual(response, ({"user": "john_doe", "room": "Conference Room 1", "date": "2023-05-28", "time-span": "10:00 - 11:00"}, 200))

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    def test_delete_reservation_success(self, mock_query):
        # Mocking the Reservation object
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.user_id = 1

        # Mocking the query filter
        mock_query.filter_by.return_value.first.return_value = mock_reservation

        # Mocking the User object
        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        response = reservation_id_resource.delete(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "Reservation deleted successfully")

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    @patch('src.resources.reservation.Room.query')
    @patch('src.resources.reservation.db')
    def test_put_reservation_success(self, mock_db, mock_room_query, mock_reservation_query):
        # Mocking the Reservation object
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.user_id = 1
        mock_reservation.start_time = MagicMock()
        mock_reservation.end_time = MagicMock()
        mock_reservation.room = MagicMock(spec=Room)

        # Mocking the query filter
        mock_reservation_query.filter_by.return_value.first.return_value = mock_reservation

        # Mocking the Room object
        mock_room = MagicMock(spec=Room)
        mock_room_query.filter_by.return_value.first.return_value = mock_room

        # Mocking the User object
        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        with self.app.test_request_context(json={"date": "2024-06-01", "start-time": "14:00", "end-time": "16:00", "roomId": 2}):
            response = reservation_id_resource.put(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "Reservation updated successfully")

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    def test_get_reservation_not_found(self, mock_query):
        mock_query.filter_by.return_value.first.return_value = None

        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        response = reservation_id_resource.get(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "No reservation found with the provided reservationId.")

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    def test_get_reservation_not_belong_to_user(self, mock_query):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.user_id = 2

        mock_query.filter_by.return_value.first.return_value = mock_reservation

        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        response = reservation_id_resource.get(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "Reservation does not belong to the provided userId.")

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    def test_delete_reservation_not_found(self, mock_query):
        mock_query.filter_by.return_value.first.return_value = None

        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        response = reservation_id_resource.delete(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "No reservation found with the provided reservationId.")

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    def test_delete_reservation_not_belong_to_user(self, mock_query):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.user_id = 2

        mock_query.filter_by.return_value.first.return_value = mock_reservation

        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        response = reservation_id_resource.delete(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "Reservation does not belong to the provided userId.")

    @patch('src.resources.reservation.check_api_key', new=dummy_check_api_key)
    @patch('src.resources.reservation.Reservation.query')
    @patch('src.resources.reservation.Room.query')
    @patch('src.resources.reservation.db')
    def test_put_reservation_room_not_found(self, mock_db, mock_room_query, mock_reservation_query):
        mock_reservation = MagicMock(spec=Reservation)
        mock_reservation.user_id = 1

        mock_reservation_query.filter_by.return_value.first.return_value = mock_reservation

        mock_room_query.filter_by.return_value.first.return_value = None

        mock_user = MagicMock()
        mock_user.id = 1

        reservation_id_resource = ReservationId()
        with self.app.test_request_context(json={"date": "2024-06-01", "start-time": "14:00", "end-time": "16:00", "roomId": 2}):
            response = reservation_id_resource.put(mock_user, 1, 1)

        self.assertEqual(response.get_data(as_text=True), "No room found with the provided roomId.")

class TestReservation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.reservation = ReservationId()

    def tearDown(self):
        self.app_context.pop()

    @patch('src.models.Reservation.query')
    def test_get_reservation(self, mock_query):
        # Setup mock objects
        mock_user = User(id=1)
        mock_room = Room(id=1)
        mock_reservation = Reservation(id=1, user_id=1, room_id=1, start_time='2022-12-01 10:00:00', end_time='2022-12-01 11:00:00')
        mock_query.filter_by.return_value.first.return_value = mock_reservation

        # Call the method under test
        response = self.reservation.get(mock_user, 1, 1)
        result = response.get_json() if response else None

        # Assert the expected results
        if result:
            self.assertEqual(result['id'], 1)
            self.assertEqual(result['user_id'], 1)
            self.assertEqual(result['room_id'], 1)
            self.assertEqual(result['start_time'], '2022-12-01 10:00:00')
            self.assertEqual(result['end_time'], '2022-12-01 11:00:00')

    @patch('src.models.Reservation.query')
    @patch('src.models.db.session.delete')
    @patch('src.models.db.session.commit')
    def test_delete_reservation(self, mock_commit, mock_delete, mock_query):
        # Setup mock objects
        mock_user = User(id=1)
        mock_reservation = Reservation(id=1, user_id=1, room_id=1, start_time='2022-12-01 10:00:00', end_time='2022-12-01 11:00:00')
        mock_query.filter_by.return_value.first.return_value = mock_reservation

        # Call the method under test
        result = self.reservation.delete(mock_user, 1)

        # Assert the expected results
        if mock_delete.called:
            mock_delete.assert_called_once_with(mock_reservation)
            mock_commit.assert_called_once()
            self.assertEqual(result, {'message': 'Reservation deleted'})

    @patch('src.models.Reservation.query')
    @patch('src.models.db.session.commit')
    def test_put_reservation(self, mock_commit, mock_query):
        # Setup mock objects
        mock_user = User(id=1)
        mock_reservation = Reservation(id=1, user_id=1, room_id=1, start_time='2022-12-01 10:00:00', end_time='2022-12-01 11:00:00')
        mock_query.filter_by.return_value.first.return_value = mock_reservation

        # Call the method under test
        response = self.reservation.put(mock_user, 1, {'start_time': '2022-12-01 12:00:00', 'end_time': '2022-12-01 13:00:00'})
        result = response.get_json() if response else None

        # Assert the expected results
        if result and mock_commit.called:
            mock_commit.assert_called_once()
            self.assertEqual(result['start_time'], '2022-12-01 12:00:00')
            self.assertEqual(result['end_time'], '2022-12-01 13:00:00')

class TestUserCollection(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_users(self):
        # Add test users
        user1 = User(username='user1', email='user1@example.com')
        user2 = User(username='user2', email='user2@example.com')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        # Check that the response contains the usernames of the added users

    def test_post_user(self):
        response = self.client.post('/users', json={
            'username': 'user3',
            'email': 'user3@example.com'
        })
        self.assertEqual(response.status_code, 201)
        # Check that the user was added to the database

class TestUserId(unittest.TestCase):
    # ...setUp and tearDown methods...

    def test_get_user(self):
        # Add a test user
        user = User(username='user', email='user@example.com')
        db.session.add(user)
        db.session.commit()

        response = self.client.get(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        # Check that the response contains the correct user information

    def test_put_user(self):
        # Add a test user
        user = User(username='user', email='user@example.com')
        db.session.add(user)
        db.session.commit()

        response = self.client.put(f'/users/{user.id}', json={
            'username': 'newuser',
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        # Check that the user information was updated in the database

    def test_delete_user(self):
        # Add a test user
        user = User(username='user', email='user@example.com')
        db.session.add(user)
        db.session.commit()

        response = self.client.delete(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        # Check that the user was deleted from the database

class TestRoomsAvailable(unittest.TestCase):
    # ...setUp and tearDown methods...

    def test_get_rooms(self):
        # Add test rooms and reservations
        # ...

        response = self.client.get('/rooms_available', query_string={
            'date': '2024-06-30',
            'time': '14:00',
            'duration': 120
        })
        self.assertEqual(response.status_code, 200)
        # Check that the response contains the correct list of available rooms

        @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_get_reservation_success(self, mock_require_user, mock_filter_by):
        # Set up mock user and reservation
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation = MagicMock(spec=Reservation, user_id=1, serialize=MagicMock(return_value={"reservation": "data"}))
        mock_filter_by.return_value.first.return_value = mock_reservation
        mock_require_user.return_value = mock_user

        response = self.client.get('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"reservation": "data"})

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_get_reservation_invalid_user_id(self, mock_require_user, mock_filter_by):
        response = self.client.get('/users/abc/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid userId parameter", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_get_reservation_user_not_authorized(self, mock_require_user, mock_filter_by):
        mock_user = MagicMock(spec=User, id=2)
        mock_require_user.return_value = mock_user

        response = self.client.get('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("The provided Api-key does not correspond to the userId provided.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_get_reservation_not_found(self, mock_require_user, mock_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_filter_by.return_value.first.return_value = None
        mock_require_user.return_value = mock_user

        response = self.client.get('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("No reservation found with the provided reservationId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_get_reservation_not_belongs_to_user(self, mock_require_user, mock_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation = MagicMock(spec=Reservation, user_id=2)
        mock_filter_by.return_value.first.return_value = mock_reservation
        mock_require_user.return_value = mock_user

        response = self.client.get('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 403)
        self.assertIn("Reservation does not belong to the provided userId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    @patch('src.resources.reservation.db.session.delete')
    @patch('src.resources.reservation.db.session.commit')
    def test_delete_reservation_success(self, mock_commit, mock_delete, mock_require_user, mock_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation = MagicMock(spec=Reservation, user_id=1)
        mock_filter_by.return_value.first.return_value = mock_reservation
        mock_require_user.return_value = mock_user

        response = self.client.delete('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Reservation deleted successfully", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    @patch('src.resources.reservation.db.session.delete')
    @patch('src.resources.reservation.db.session.commit')
    def test_delete_reservation_not_found(self, mock_commit, mock_delete, mock_require_user, mock_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_filter_by.return_value.first.return_value = None
        mock_require_user.return_value = mock_user

        response = self.client.delete('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("No reservation found with the provided reservationId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_delete_reservation_not_belongs_to_user(self, mock_require_user, mock_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation = MagicMock(spec=Reservation, user_id=2)
        mock_filter_by.return_value.first.return_value = mock_reservation
        mock_require_user.return_value = mock_user

        response = self.client.delete('/users/1/reservations/1', headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 403)
        self.assertIn("Reservation does not belong to the provided userId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.Room.query.filter_by')
    @patch('src.resources.reservation.require_user')
    @patch('src.resources.reservation.db.session.commit')
    def test_put_reservation_success(self, mock_commit, mock_require_user, mock_room_filter_by, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_room = MagicMock(spec=Room, id=2, max_time=180)
        mock_reservation = MagicMock(spec=Reservation, user_id=1, start_time=datetime(2024, 6, 1, 10, 0), end_time=datetime(2024, 6, 1, 12, 0), room=mock_room)
        mock_reservation_filter_by.return_value.first.return_value = mock_reservation
        mock_room_filter_by.return_value.first.return_value = mock_room
        mock_require_user.return_value = mock_user

        response = self.client.put('/users/1/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 2
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Reservation updated successfully", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_invalid_user_id(self, mock_require_user, mock_reservation_filter_by):
        response = self.client.put('/users/abc/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 2
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid userId parameter", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_user_not_authorized(self, mock_require_user, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=2)
        mock_require_user.return_value = mock_user

        response = self.client.put('/users/1/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 2
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("The provided Api-key does not correspond to the userId provided.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_not_found(self, mock_require_user, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation_filter_by.return_value.first.return_value = None
        mock_require_user.return_value = mock_user

        response = self.client.put('/users/1/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 2
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("No reservation found with the provided reservationId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_not_belongs_to_user(self, mock_require_user, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation = MagicMock(spec=Reservation, user_id=2)
        mock_reservation_filter_by.return_value.first.return_value = mock_reservation
        mock_require_user.return_value = mock_user

        response = self.client.put('/users/1/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 2
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 403)
        self.assertIn("Reservation does not belong to the provided userId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.Room.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_invalid_room(self, mock_require_user, mock_room_filter_by, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_reservation = MagicMock(spec=Reservation, user_id=1)
        mock_reservation_filter_by.return_value.first.return_value = mock_reservation
        mock_room_filter_by.return_value.first.return_value = None
        mock_require_user.return_value = mock_user

        response = self.client.put('/users/1/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 999
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("No room found with the provided roomId.", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.Room.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_time_slot_taken(self, mock_require_user, mock_room_filter_by, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_room = MagicMock(spec=Room, id=2, max_time=180)
        mock_reservation = MagicMock(spec=Reservation, user_id=1, start_time=datetime(2024, 6, 1, 10, 0), end_time=datetime(2024, 6, 1, 12, 0), room=mock_room)
        mock_overlapping_reservation = MagicMock(spec=Reservation, user_id=1, start_time=datetime(2024, 6, 1, 14, 0), end_time=datetime(2024, 6, 1, 16, 0), room=mock_room)
        mock_reservation_filter_by.return_value.first.return_value = mock_reservation
        mock_room_filter_by.return_value.first.return_value = mock_room

        with patch('src.resources.reservation.Reservation.query.filter', return_value=[mock_overlapping_reservation]):
            response = self.client.put('/users/1/reservations/1', json={
                "date": "2024-06-01",
                "start-time": "14:00",
                "end-time": "16:00",
                "roomId": 2
            }, headers={"Api-key": "valid_key"})
            self.assertEqual(response.status_code, 409)
            self.assertIn("Time slot already taken", response.data.decode())

    @patch('src.resources.reservation.Reservation.query.filter_by')
    @patch('src.resources.reservation.Room.query.filter_by')
    @patch('src.resources.reservation.require_user')
    def test_put_reservation_too_long(self, mock_require_user, mock_room_filter_by, mock_reservation_filter_by):
        mock_user = MagicMock(spec=User, id=1)
        mock_room = MagicMock(spec=Room, id=2, max_time=60)
        mock_reservation = MagicMock(spec=Reservation, user_id=1, start_time=datetime(2024, 6, 1, 10, 0), end_time=datetime(2024, 6, 1, 12, 0), room=mock_room)
        mock_reservation_filter_by.return_value.first.return_value = mock_reservation
        mock_room_filter_by.return_value.first.return_value = mock_room
        mock_require_user.return_value = mock_user

        response = self.client.put('/users/1/reservations/1', json={
            "date": "2024-06-01",
            "start-time": "14:00",
            "end-time": "16:00",
            "roomId": 2
        }, headers={"Api-key": "valid_key"})
        self.assertEqual(response.status_code, 409)
        self.assertIn("Reservation is too long.", response.data.decode())

    def test_get_reservation_success(self, mock_get_user):
        @patch('src.resources.reservation.get_user_by_api_key', side_effect=self.mock_get_user)

        # Test successful retrieval of a reservation
        reservation_id = ReservationId()
        response = reservation_id.get(self.user.api_key, self.user.id, self.reservation.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["user"], "john_doe")
        self.assertEqual(response.json["room"], "Conference Room 1")
        self.assertEqual(response.json["date"], "2024-06-28")
        self.assertEqual(response.json["time-span"], "10:00 - 11:00")

    @patch('src.resources.reservation.get_user_by_api_key', side_effect=self.mock_get_user)
    def test_get_reservation_invalid_user_id(self, mock_get_user):
        # Test with invalid user ID
        reservation_id = ReservationId()
        response = reservation_id.get(self.user.api_key, 100, self.reservation.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, "Invalid userId parameter")

    @patch('src.resources.reservation.get_user_by_api_key', return_value=None)
    def test_get_reservation_wrong_api_key(self, mock_get_user):
        # Test with wrong API key
        reservation_id = ReservationId()
        response = reservation_id.get("invalid_api_key", self.user.id, self.reservation.id)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, "The provided Api-key does not correspond to the userId provided.")

    @patch('src.resources.reservation.get_user_by_api_key', side_effect=self.mock_get_user)
    def test_get_reservation_not_found(self, mock_get_user):
        # Test with non-existent reservation ID
        reservation_id = ReservationId()
        response = reservation_id.get(self.user.api_key, self.user.id, 100)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, "No reservation found with the provided reservationId.")

    @patch('src.resources.reservation.get_user_by_api_key', side_effect=self.mock_get_user)
    def test_get_reservation_permission_denied(self, mock_get_user):
        # Test trying to access another user's reservation
        another_user = User(2, "jane_doe", "password2")
        db

if __name__ == '__main__':
    unittest.main()
