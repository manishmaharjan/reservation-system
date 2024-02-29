from . import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
import hashlib
import secrets

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    reservations = db.relationship('Reservation', back_populates='user', cascade='all, delete-orphan')
    api_keys = db.relationship('ApiKey', back_populates='user', cascade='all, delete-orphan')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    max_time = db.Column(db.Integer, nullable=False, default = 180) # Maximun reservation time in minutes

    reservations = db.relationship('Reservation', back_populates ='room', cascade='all, delete-orphan')
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('room_id', 'start_time', 'end_time'),
    )

    room = db.relationship('Room', back_populates = 'reservations')
    user = db.relationship('User', back_populates = 'reservations')

    def serialize(self):
        doc = {
            "user": self.user.username,
            "room": self.room.room_name,
            "date": self.start_time.date().isoformat(),
            "time-span": f"{self.start_time.time()} - {self.end_time.time()}"
        }
        return doc

# Got the code from https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/implementing-rest-apis-with-flask/#validating-keys
class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), nullable=False, unique=True)
    admin = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='api_keys')
    @staticmethod
    def key_hash(key):
        return hashlib.sha256(key.encode()).digest()
    
    def create_token(self):
        return secrets.token_urlsafe() 

