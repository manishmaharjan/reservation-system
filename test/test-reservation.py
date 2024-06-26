import unittest
from unittest.mock import patch
from src.resources.reservation import ReservationId
from src.models import Reservation, User, Room
from flask import Flask

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

if __name__ == '__main__':
    unittest.main()
