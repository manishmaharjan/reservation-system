import pytest
import json
from flask import Request, Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta, datetime, time
from src.resources.user import RegisterUser
from src.models import Room, Reservation, User, db

class TestReservation:

    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        with app.app_context():
            db.init_app(app)
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def setup_method(self):
        # Set up initial configuration for tests
        self.register_user = RegisterUser()

    def teardown_method(self):
        # Clean up after each test
        pass

    def test_get_reservations(self, client):
        # Mock user and reservations
        user1 = User(username='user1', email='user1@example.com')
        user2 = User(username='user2', email='user2@example.com')
        room1 = Room(room_name='Room 1', capacity=10)
        room2 = Room(room_name='Room 2', capacity=20)
        reservation_1 = Reservation(room=room1, user=user1, date=date.today(), start_time=time(9, 0), end_time=time(10, 0))
        reservation_2 = Reservation(room=room2, user=user2, date=date.today(), start_time=time(11, 0), end_time=time(12, 0))
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(room1)
        db.session.add(room2)
        db.session.add(reservation_1)
        db.session.add(reservation_2)
        db.session.commit()

        # Make request
        response = client.get('/reservations')
        data = json.loads(response.data.decode('utf-8'))

        # Assertions
        assert response.status_code == 200
        assert len(data) == 2

    def test_create_reservation(self, client):
        # Mock user and room
        user = User(username='user1', email='user1@example.com')
        room = Room(room_name='Room 1',capacity=10)
        db.session.add(user)
        db.session.add(room)
        db.session.commit()

        # Mock request data
        data = {
            'date': str(datetime.now().date()),
            'start_time': '10:00',
            'end_time': '12:00'
        }

        # Make request
        response = client.post('/reservations', json=data)

        # Assertions
        assert response.status_code == 209

    def test_delete_reservation(self, client):
        # Mock user, room, and reservation
        user1 = User(username='user1', email='user1@example.com')
        room1 = Room(room_name='Room 1', capacity=10)
        reservation_1 = Reservation(room=room1, user=user1, date=date.today(), start_time=time(9, 0), end_time=time(10, 0))
        db.session.add(user1)
        db.session.add(room1)
        db.session.add(reservation_1)
        db.session.commit()

        # Make request
        response = client.delete(f'/reservations/{reservation_1.id}')

        # Assertions
        assert response.status_code == 204

    def test_get_reservation_list(self, client):
        # Mock reservations
        user1 = User(username='user1', email='user1@example.com')
        user2 = User(username='user2', email='user2@example.com')
        room1 = Room(room_name='Room 1', capacity=10)
        room2 = Room(room_name='Room 2', capacity=20)
        reservation_1 = Reservation(room=room1, user=user1, date=date.today(), start_time=time(9, 0), end_time=time(10, 0))
        reservation_2 = Reservation(room=room2, user=user2, date=date.today(), start_time=time(11, 0), end_time=time(12, 0))
        db.session.add(reservation_1)
        db.session.add(reservation_2)
        db.session.commit()

        # Make request
        response = client.get('/reservations/list')
        data = json.loads(response.data.decode('utf-8'))

        # Assertions
        assert response.status_code == 200
        assert len(data) == 2
