import pytest
from flask import Flask
from src.models import Room, Reservation, User, db
from src.resources.reservation import GetReservations, CreateReservation, DeleteReservation
from datetime import datetime, timedelta
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()



def test_get_reservations(app, client):
    with app.test_request_context('/'):
        # Mocking user and room objects
        user = MagicMock(spec=User)
        room = MagicMock(spec=Room)

        # Creating reservations
        now = datetime.now()
        reservation1 = MagicMock(spec=Reservation, start_time=now, end_time=now + timedelta(hours=1))
        reservation2 = MagicMock(spec=Reservation, start_time=now, end_time=now + timedelta(hours=2))
        reservations = [reservation1, reservation2]

        # Mocking the query method of Reservation
        Reservation.query.filter_by().all.return_value = reservations

        response = client.get('/get_reservations?start_date=2024-01-01&end_date=2024-12-31')

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json == [reservation.serialize.return_value for reservation in reservations]

def test_create_reservation(app, client):
    with app.test_request_context('/', method='POST', json={
        'date': '2024-03-01',
        'start_time': '10:00',
        'end_time': '11:00'
    }):
        # Mocking user and room objects
        user = MagicMock(spec=User)
        room = MagicMock(spec=Room)

        # Mocking overlapping_reservations
        overlaping_reservations = [MagicMock(spec=Reservation)]
        Reservation.query.filter().all.return_value = overlaping_reservations

        response = client.post('/create_reservation')

        assert response.status_code == 209
        assert Reservation.query.count() == 1

def test_delete_reservation(app, client):
    with app.test_request_context('/', method='DELETE'):
        # Create users and rooms in the database
        user1 = User(username='user1', email='user1@example.com')
        room1 = Room(room_name='Room 1', capacity=10)
        db.session.add(user1)
        db.session.add(room1)
        db.session.commit()

        # Create a reservation to delete
        reservation = Reservation(room=room1, user=user1, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=1))
        db.session.add(reservation)
        db.session.commit()

        # Delete the reservation using its ID
        response = client.delete(f'/delete_reservation/{reservation.id}')

        # Ensure the response is correct
        assert response.status_code == 204

        # Ensure the reservation has been deleted from the database
        assert Reservation.query.count() == 0

