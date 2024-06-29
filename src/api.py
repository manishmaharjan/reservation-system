"""
This module provides the API endpoints for the reservation system.
"""

from flasgger import Swagger
from flask_restful import Api

from src import create_app

from .converters import RoomConverter
from .resources import (
    reservation,
    reservationCollection,
    rooms_available,
    user,
    userCollection,
)

app = create_app()

swagger = Swagger(app)

api = Api(app)

app.url_map.converters["room"] = RoomConverter

api.add_resource(userCollection.UserCollection, "/api/users/")
api.add_resource(user.UserId, "/api/users/<userId>/")

api.add_resource(
    reservationCollection.ReservationCollection, "/api/users/<userId>/reservations/"
)
api.add_resource(
    reservation.ReservationId, "/api/users/<userId>/reservations/<reservationId>/"
)

api.add_resource(rooms_available.RoomsAvailable, "/api/rooms_available/")

if __name__ == "__main__":
    app.run(debug=True)
