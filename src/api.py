"""
This module provides the API endpoints for the reservation system.
"""

from flasgger import Swagger
from flask_restful import Api

from . import create_app
from .converters import RoomConverter
from .resources import (
    reservation,
    reservation_collection,
    rooms_available,
    user,
    user_collection,
)

app = create_app()

swagger = Swagger(app)

api = Api(app)

app.url_map.converters["room"] = RoomConverter

api.add_resource(user_collection.UserCollection, "/api/users/")
api.add_resource(user.UserId, "/api/users/<user_id>/")

api.add_resource(
    reservation_collection.ReservationCollection, "/api/users/<user_id>/reservations/"
)
api.add_resource(
    reservation.ReservationId, "/api/users/<user_id>/reservations/<reservation_id>/"
)

api.add_resource(rooms_available.RoomsAvailable, "/api/rooms_available/")

if __name__ == "__main__":
    app.run(debug=True)
