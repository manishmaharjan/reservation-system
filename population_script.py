
"""
This script is used to populate the database with initial data for a reservation system.
"""

from datetime import date, datetime, time
from src.api import app
from src.models import ApiKey, Reservation, Room, User, db


# Obtain the application context
app_ctx = app.app_context()
# Push the application context to activate it
app_ctx.push()

# Inside the context, perform database operations
def populate_db( db, ctx,test = False):
    try:
        # Drop all existing tables
        db.drop_all()

        # Create tables again
        db.create_all()

        # Create users
        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")
        admin = User(username="admin", email="admin@example.com")


        # Create rooms
        room1 = Room(room_name="Room 1", capacity=10)
        room2 = Room(room_name="Room 2", capacity=20)

        token1 = "Z9udK8CT3Bv_ssND85CXA6qFJBVf6lhIEMDW9sficC4"  # ApiKey.create_token()
        token2 = "cLENKIlIT39h18gbAkSBNNAjyOTCVUlF5iCUbHnqJBo"  # ApiKey.create_token()
        adminTok = "ddMM0fJfmMBxCt0WdZoqqPKKHuZwptdtgE6-3cYUEns"  # ApiKey.create_token()

        api_key1 = ApiKey(key=ApiKey.key_hash(token1), user=user1)
        api_key2 = ApiKey(key=ApiKey.key_hash(token2), user=user2)
        api_key_admin = ApiKey(key=ApiKey.key_hash(adminTok), user=admin, admin = True)

        

        # Create reservations
        reservation1 = Reservation(
            room=room1,
            user=user1,
            start_time=datetime.combine(date.today(), time(9, 2)),
            end_time=datetime.combine(date.today(), time(10, 2)),
        )
        reservation2 = Reservation(
            room=room2,
            user=user2,
            start_time=datetime.combine(date.today(), time(11, 2)),
            end_time=datetime.combine(date.today(), time(12, 2)),
        )

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
        if test:
            userTest = User(username="testAdminUser", email="test@test.com")
            tokTest = "aa" # For the admin testing
            api_test = ApiKey(key = ApiKey.key_hash(tokTest), user= userTest, admin = True)
            db.session.add(api_test)
            db.session.add(userTest)

        # Commit the changes to the database
        db.session.commit()
    finally:
        # Remove the application context when done
        ctx.pop()

populate_db(db,app_ctx)
