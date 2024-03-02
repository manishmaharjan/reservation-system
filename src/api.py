"""
This module provides the API endpoints for the reservation system.
"""

from flask_restful import Api

from src import create_app

from .converters import RoomConverter
from .resources import reservation, user

app = create_app()

api = Api(app)

app.url_map.converters["room"] = RoomConverter

api.add_resource(user.RegisterUser, "/api/user/register/")
api.add_resource(reservation.GetReservations, "/api/reservations/")
api.add_resource(reservation.CreateReservation, "/api/reservations/<room:room>/")
api.add_resource(
    reservation.DeleteReservation, "/api/reservations/<room:room>/<int:reservation_id>/"
)
