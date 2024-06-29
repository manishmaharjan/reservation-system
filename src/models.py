"""
This module contains the database models for the reservation system.

It defines the following classes:
- User: Represents a user in the reservation system.
- Room: Represents a room in the reservation system.
- Reservation: Represents a reservation made by a user for a specific room.
- ApiKey: Represents an API key in the reservation system.
"""

import hashlib
import secrets

from sqlalchemy import event
from sqlalchemy.engine import Engine

from src import db


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record=None):
    """
    Set the SQLite pragma to enable foreign key constraints.

    Args:
        dbapi_connection: The SQLite database connection.

    Returns:
        None
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(db.Model):
    # pylint: disable=too-few-public-methods
    """
    Represents a user in the reservation system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        reservations (list): A list of reservations made by the user.
        api_keys (list): A list of API keys associated with the user.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    reservations = db.relationship(
        "Reservation", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys = db.relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )

    def serialize(self):
        """
        Serialize the user object into a dictionary.

        Returns:
            dict: A dictionary representation of the user object.
        """
        doc = {"id": self.id, "username": self.username, "email": self.email}
        return doc


class Room(db.Model):
    # pylint: disable=too-few-public-methods
    """
    Represents a room in the reservation system.

    Attributes:
        id (int): The unique identifier for the room.
        room_name (str): The name of the room.
        capacity (int): The maximum capacity of the room.
        max_time (int): The maximum reservation time in minutes.
        reservations (list): The list of reservations associated with the room.
    """

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    max_time = db.Column(db.Integer, nullable=False, default=180)

    reservations = db.relationship(
        "Reservation", back_populates="room", cascade="all, delete-orphan"
    )

    def serialize(self):
        """
        Serialize the room object into a dictionary.

        Returns:
            dict: A dictionary representation of the room object.
        """
        doc = {
            "id": self.id,
            "room_name": self.room_name,
            "capacity": self.capacity,
            "max_time": self.max_time,
        }
        return doc


class Reservation(db.Model):
    # pylint: disable=too-few-public-methods
    """
    Represents a reservation made by a user for a specific room.

    Attributes:
        id (int): The unique identifier for the reservation.
        room_id (int): The ID of the room being reserved.
        user_id (int): The ID of the user making the reservation.
        start_time (datetime): The start time of the reservation.
        end_time (datetime): The end time of the reservation.
        room (Room): The room object associated with the reservation.
        user (User): The user object associated with the reservation.
    """

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(
        db.Integer, db.ForeignKey("room.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    __table_args__ = (db.UniqueConstraint("room_id", "start_time", "end_time"),)

    room = db.relationship("Room", back_populates="reservations")
    user = db.relationship("User", back_populates="reservations")

    def serialize(self):
        """
        Serialize the reservation object into a dictionary.

        Returns:
            dict: A dictionary representation of the reservation object.
        """
        doc = {
            "id": self.id,
            "user": self.user.username,
            "room": self.room.room_name,
            "date": self.start_time.date().isoformat(),
            "time-span": f"{self.start_time.time()} - {self.end_time.time()}",
        }
        return doc


# Got the code from
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/#validating-keys
class ApiKey(db.Model):
    # pylint: disable=too-few-public-methods
    """
    Represents an API key in the reservation system.

    Attributes:
        id (int): The unique identifier of the API key.
        key (str): The API key value.
        admin (bool): Indicates whether the API key has admin privileges.
        user_id (int): The foreign key referencing the associated user.
        user (User): The user associated with the API key.

    Methods:
        key_hash(key): Hashes the given key using SHA-256 algorithm.
        create_token(): Generates a URL-safe token using the secrets module.
    """

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), nullable=False, unique=True)
    admin = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="api_keys")

    @staticmethod
    def key_hash(key):
        """
        Hashes the given key using SHA-256 algorithm.

        Args:
            key (str): The key to be hashed.

        Returns:
            bytes: The hashed key as bytes.

        """
        return hashlib.sha256(key.encode()).digest()

    def create_token(self):
        """
        Generates a URL-safe token using the secrets module.

        Returns:
            str: A URL-safe token.
        """
        return secrets.token_urlsafe()
