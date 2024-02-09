from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User, Room, Reservation, Facility

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservation_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)




