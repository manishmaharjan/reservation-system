"""
This module provides the API endpoints for the reservation system.
"""

from flasgger import Swagger
from flask_restful import Api

from src import create_app

from .converters import RoomConverter
from .resources import reservation, reservationCollection,  userCollection, user, rooms_available

app = create_app()


def prepare_api(app):
    '''
    Function to configure the app on the test instance.

    '''
    swagger = Swagger(app)

    api = Api(app)

    app.url_map.converters["room"] = RoomConverter

    api.add_resource(userCollection.UserCollection, "/api/users/")
    api.add_resource(user.UserId, "/api/users/<userId>/")

    api.add_resource(reservationCollection.ReservationCollection, "/api/users/<userId>/reservations/")
    api.add_resource(reservation.ReservationId, "/api/users/<userId>/reservations/<reservationId>/")

    api.add_resource(rooms_available.RoomsAvailable, "/api/rooms_available/")
prepare_api(app)

if __name__ == "__main__":
    app.run(debug=True)

