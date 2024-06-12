"""
This module contains the implementation of the ReservationCollection resource.

The ReservationCollection resource is responsible for handling the creation of new reservations. It provides
an endpoint for creating a new reservation by accepting a JSON payload containing the date, time and the id of the room 
that will be booked. With another endpoint to get a list of all the users. 

Classes:
    ReservationCollection: A resource class for creating new reservations and getting a list of all reservations of the user.

"""


from flask import Response, request
from flask_restful import Resource
from ..decorators import require_user

class ReservationCollection(Resource):
    """
    Resource class for creating a new reservation or getting a list of all the reservations of an user.

    This class handles the POST request for creating a new reservation. It expects JSON data
    containing the date, time and id of the room. It checks that there is no other reservation 
    at that time and date in that room, and thenc reates the reservation object.
    It also handles a GET request which gets a list of all the reservations of the user, and returns it. 

    Attributes:
        None

    Methods:
        get(userId): Handles the GET request for returning a list with all the reservations of the user.
        post(userId): Handles the POST request for registering a new user.

    """
    @require_user
    def get(self,userId)
    
