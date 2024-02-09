from datetime import time, date
from models import Room,Reservation,User, db
from app import app

ctx = app.app_context()
ctx.push()
db.create_all()

user1 = User(username='user1', email='user1@example.com', password='password1')
user2 = User(username='user2', email='user2@example.com', password='password2')

# Create rooms
room1 = Room(room_name='Room 1', capacity=10)
room2 = Room(room_name='Room 2', capacity=20)


# Create reservations
reservation1 = Reservation(room=room1, user=user1, date=date.today(), start_time=time(9, 0), end_time=time(10, 0))
reservation2 = Reservation(room=room2, user=user2, date=date.today(), start_time=time(11, 0), end_time=time(12, 0))

# Add objects to the session
db.session.add(user1)
db.session.add(user2)
db.session.add(room1)
db.session.add(room2)
db.session.add(reservation1)
db.session.add(reservation2)

# Commit the changes to the database
db.session.commit()


