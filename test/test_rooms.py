from test.test_config import client
from .utils import create_reservation, delete_reservation, create_user
import json
from src.converters import RoomConverter
from src import db
from src.models import Room

def test_params(client):
    date = "2024-06-28"
    time = "11:00"
    response = client.get(f"/api/rooms_available/?date={date}")

    assert response.status_code == 400
    assert response.text == "date and time parameters are required."

    response = client.get(f"/api/rooms_available/?time={time}")

    assert response.status_code == 400
    assert response.text == "date and time parameters are required."
    
    response = client.get(f"/api/rooms_available/")

    assert response.status_code == 400
    assert response.text == "date and time parameters are required."

def test_invalid_params(client):
    date = "2024-06:28"
    time = "11:00"
    response = client.get(f"/api/rooms_available/?date={date}&time={time}")

    assert response.status_code == 400
    assert response.text == "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."

    date = "invalid"
    time = "11:00"
    response = client.get(f"/api/rooms_available/?date={date}&time={time}")

    assert response.status_code == 400
    assert response.text == "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
    
    date = "2024-06:28"
    time = "invalid"
    response = client.get(f"/api/rooms_available/?date={date}&time={time}")

    assert response.status_code == 400
    assert response.text == "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."

def test_invalid_duration(client):
    date = "2024-06-28"
    time = "11:00"
    duration = -1
    response = client.get(f"/api/rooms_available/?date={date}&time={time}&duration={duration}")

    assert response.status_code == 400
    assert response.text == "Duration must be a positive integer."

    response = client.get(f"/api/rooms_available/?date={date}&time={time}&duration=invalid")

    assert response.status_code == 400
    assert response.text == "Duration must be a positive integer."

def test_correct_request(client):
    date = "2024-07-18"
    time = "11:00"
    duration = 2
    response = client.get(f"/api/rooms_available/?date={date}&time={time}&duration={duration}")

    rooms = json.loads(response.data)['available_rooms']

    assert response.status_code == 200
    assert len(rooms) == 2

def test_duration_parameter(client):
    # The available time slot will be smaller than the duration during that time slot
    api_key, user_id = create_user(client)
    date = "2024-07-18"
    
    create_reservation(client,api_key, user_id,date, "9:00", "10:00", 1)
    create_reservation(client,api_key, user_id,date, "10:15","12:00", 1)

    create_reservation(client,api_key, user_id,date, "9:00", "10:00", 2)
    create_reservation(client,api_key, user_id,date, "10:30","12:00", 2)

    response = client.get(f"/api/rooms_available/?date={date}&time=10:00")

    rooms = json.loads(response.data)['available_rooms']

    assert response.status_code == 200
    assert len(rooms) == 0

    duration = 5
    response = client.get(f"/api/rooms_available/?date={date}&time=10:05&duration={duration}")

    rooms = json.loads(response.data)['available_rooms']

    assert response.status_code == 200
    assert len(rooms) == 2

    duration = 15
    response = client.get(f"/api/rooms_available/?date={date}&time=10:05&duration={duration}")

    rooms = json.loads(response.data)['available_rooms']

    assert response.status_code == 200
    assert len(rooms) == 1

    duration = 30
    response = client.get(f"/api/rooms_available/?date={date}&time=10:05&duration={duration}")

    rooms = json.loads(response.data)['available_rooms']

    assert response.status_code == 200
    assert len(rooms) == 0


def test_to_python_success(client):
    # Add a sample room to the database
    room = Room(id=5, room_name="Conference Room", capacity=10, max_time=120)
    db.session.add(room)
    db.session.commit()

    converter = RoomConverter(None)
    result = converter.to_python(5)

    assert result.id == room.id
    assert result.room_name == room.room_name
    assert result.capacity == room.capacity
    assert result.max_time == room.max_time

    # Clean up
    db.session.delete(room)
    db.session.commit()

def test_to_python_not_found(client):
    converter = RoomConverter(None)
    invalid_room_id = 999

    try:
        converter.to_python(invalid_room_id)
    except Exception as e:
        assert str(e) ==  "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."

def test_to_url_success(client):
    # Add a sample room to the database
    room = Room(id=6, room_name="Conference Room", capacity=10, max_time=120)
    db.session.add(room)
    db.session.commit()

    converter = RoomConverter(None)
    result = converter.to_url(room)

    assert result == room.id

    # Clean up
    db.session.delete(room)
    db.session.commit()