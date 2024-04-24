"""
This module provides the API endpoints for the reservation system.
"""

from flasgger import Swagger
from flask_restful import Api
from flask import Blueprint
from .resources import reservation,user
from .converters import RoomConverter

def setup_routes(app):
    " Initialize API with Swagger documentation"
    swagger = Swagger(app)
    api = Api(app)

    # Adding custom URL converters
    app.url_map.converters["room"] = RoomConverter

    # Registering API resources
    api.add_resource(user.RegisterUser, "/api/user/register/")
    api.add_resource(reservation.GetReservations, "/api/reservations/")
    api.add_resource(reservation.CreateReservation, "/api/reservations/<room:room>/")
    api.add_resource(reservation.DeleteReservation, "/api/reservations/<room:room>/<int:reservation_id>/")
