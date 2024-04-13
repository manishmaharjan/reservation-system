"""
This module provides the API endpoints for the reservation system.
"""

from flasgger import Swagger
from flask_restful import Api

from src import create_app

from .converters import RoomConverter
from .resources import reservation, user

app = create_app()

swagger = Swagger(app)

api = Api(app)

app.url_map.converters["room"] = RoomConverter

api.add_resource(user.RegisterUser, "/api/user/register/")
api.add_resource(reservation.GetReservations, "/api/reservations/")
api.add_resource(reservation.CreateReservation, "/api/reservations/<room:room>/")
api.add_resource(
    reservation.DeleteReservation, "/api/reservations/<room:room>/<int:reservation_id>/"
)

if __name__ == "__main__":
    app.run(debug=True)
