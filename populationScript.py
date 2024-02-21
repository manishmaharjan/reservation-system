from datetime import time, date
from src.models import Room,Reservation,User, db, ApiKey
from src.api import app
import secrets

with app.app_context() as ctx:
    ctx.push()
    db.create_all()

    user1 = User(username='user1', email='user1@example.com')
    user2 = User(username='user2', email='user2@example.com')
    admin = User(username='admin', email='admin@example.com')

    # Create rooms
    room1 = Room(room_name='Room 1', capacity=10)
    room2 = Room(room_name='Room 2', capacity=20)

    token1 = 'Z9udK8CT3Bv_ssND85CXA6qFJBVf6lhIEMDW9sficC4'
    token2 = 'cLENKIlIT39h18gbAkSBNNAjyOTCVUlF5iCUbHnqJBo'
    adminTok = 'ddMM0fJfmMBxCt0WdZoqqPKKHuZwptdtgE6-3cYUEns'
    
    api_key1 = ApiKey(key=ApiKey.key_hash(token1), user = user1)
    api_key2 = ApiKey(key=ApiKey.key_hash(token2), user = user2)
    api_key_admin = ApiKey(key=ApiKey.key_hash(adminTok), user = admin)

    # Create reservations
    reservation1 = Reservation(room=room1, user=user1, date=date.today(), start_time=time(9, 0), end_time=time(10, 0))
    reservation2 = Reservation(room=room2, user=user2, date=date.today(), start_time=time(11, 0), end_time=time(12, 0))

    # Add objects to the session
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(admin)
    db.session.add(room1)
    db.session.add(room2)
    db.session.add(reservation1)
    db.session.add(reservation2)
    db.session.add(api_key1)
    db.session.add(api_key2)
    db.session.add(api_key_admin)

    # Commit the changes to the database
    db.session.commit()


