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
from werkzeug.exceptions import UnsupportedMediaType
from datetime import date, datetime, timedelta
from src import db
from json import JSONDecodeError
from ..decorators import require_user
from ..models import Reservation, Room

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
    def get(self, apiKeyUser, userId):
        """
        Retrieve all reservations for a given user.

        This method handles GET requests to retrieve all reservations associated with a specific user.
        The request must include a valid API key in the header, and the API key must correspond to the userId provided.

        Args:
            userId (int): The unique identifier of the user for whom reservations are being retrieved.

        Returns:
            Response: A list of all reservations for the specified user, or an error message with the appropriate status code.

        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: Api-key
            type: string
            required: true
            description: The user for whom to retrieve reservations using API key for authentication.
        responses:
          200:
            description: A list of all reservations for the specified user.
            content:
              application/json:
                schema:
                  type: array
                  items:
                    type: object
                    properties:
                      user:
                        type: string
                        description: The username of the user who made the reservation.
                        example: "john_doe"
                      room:
                        type: string
                        description: The name of the reserved room.
                        example: "Conference Room A"
                      date:
                        type: string
                        format: date
                        description: The date of the reservation.
                        example: "2023-05-28"
                      time-span:
                        type: string
                        description: The time span of the reservation.
                        example: "10:00:00 - 11:00:00"
          400:
            description: Invalid userId parameter.
          401:
            description: The provided API key does not correspond to the userId provided.
        """

        # Check that the userId parameter is correct
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status = 400)
        except ValueError:
            return Response("Invalid userId parameter", status = 400)      

        # Check that the api-key corresponds to the user.
        if apiKeyUser.id != userId:
            return Response("The provided Api-key does not correspond to the userId provided.", status = 401)
        
        reservation_list = [r.serialize() for r in apiKeyUser.reservations]

        return reservation_list, 200
    
    @require_user
    def post(self, apiKeyUser, userId):
        """
        Create a new reservation for a given user.

        This method handles POST requests to create a new reservation for a specific user.
        The request must include a valid API key in the header, and the API key must correspond to the userId provided.
        The reservation details (date, start-time, end-time, roomId) must be provided in the request body in JSON format.

        Args:
            apiKeyUser (User): The user associated with the provided API key.
            userId (int): The unique identifier of the user for whom the reservation is being created.

        Returns:
            Response: A success message with status 201 if the reservation is created successfully,
                    or an error message with the appropriate status code.
        
        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: Api-key
            type: string
            required: true
            description: The user for whom to create a reservation using API key for authentication.
          - in: body
            name: reservation
            description: The reservation details.
            schema:
              type: object
              required:
                - date
                - start-time
                - end-time
                - roomId
              properties:
                date:
                  type: string
                  format: date
                  description: The date of the reservation.
                  example: "2023-05-28"
                start-time:
                  type: string
                  format: time
                  description: The start time of the reservation.
                  example: "10:00"
                end-time:
                  type: string
                  format: time
                  description: The end time of the reservation.
                  example: "11:00"
                roomId:
                  type: integer
                  description: The ID of the room being reserved.
                  example: 1
        responses:
          201:
            description: Reservation created successfully.
            headers:
              reservation_id:
                description: The id of the newly created reservation.
                schema:
                  type: integer
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Reservation created successfully"
          400:
            description: Invalid userId parameter, or missing/invalid reservation details.
          401:
            description: The provided API key does not correspond to the userId provided.
          404:
            description: No room found with the roomId provided.
          409:
            description: Reservation conflict (e.g., past time slot, overlapping reservation, reservation too long).
          415:
            description: The request body must be in JSON format.
        """

        # Check that the userId parameter is correct
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status = 400)
        except ValueError:
            return Response("Invalid userId parameter", status = 400)      

        # Check that the api-key corresponds to the user.
        if apiKeyUser.id != userId:
            return Response("The provided Api-key does not correspond to the userId provided.", status = 401)
        
        # Ensure correct json
        if not request.is_json:
            return Response("Request must be in JSON format.", status = 415)
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
            reservation_date = data.get("date")
            start_time = data.get("start-time")
            end_time = data.get("end-time")
            room_id = data.get("roomId")
        except :
            return Response(f"Error parsing JSON data", status=400)
        if not date or not start_time or not end_time or not room_id:
            return Response("date, start-time, end-time and roomId are required", status=400)
        
        # Check that the room id corresponds to a room
        room = Room.query.filter_by(id = room_id).first()
        if not room:
            return Response("No room found with the provided room id.", status = 404)
        
        # Convert reservation_date, start_time, and end_time to datetime Python objects
        try:
            reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
            start_time = datetime.combine(
                reservation_date, datetime.strptime(start_time, "%H:%M").time()
            )
            end_time = datetime.combine(
                reservation_date, datetime.strptime(end_time, "%H:%M").time()
            )
            if (
                end_time.time() <= start_time.time()
            ):  # In case the reservation is on midnight
                end_time += timedelta(days=1)
        except:
            return Response("Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM",
                status=400,
            )
        
        if start_time < datetime.now():
            return Response("Can not book past time slots", status=409)

        total_minutes = (end_time - start_time).total_seconds() // 60

        if total_minutes > room.max_time:
            return Response("Reservation is too long.", status=409)

        overlaping_reservations = Reservation.query.filter(
            (Reservation.room == room)
            & (
                (
                    (Reservation.start_time >= start_time)
                    & (Reservation.start_time <= end_time)
                )
                | (  # If a reservation starts in the timespan
                    (Reservation.end_time >= start_time)
                    & (Reservation.end_time <= end_time)
                )
                | (  # If a reservation ends in the timespan
                    (Reservation.start_time <= start_time)
                    & (Reservation.end_time >= end_time)
                )  # If the whole timespan is already booked
            )
        ).all()

        if overlaping_reservations:
            return Response("Time slot already taken", status=409)
        
        # Create and insert the object
        reservation = Reservation(
            room=room, user=apiKeyUser, start_time=start_time, end_time=end_time
        )
        db.session.add(reservation)
        db.session.commit()

        return Response("Reservation created successfully", headers={"reservation_id": reservation.id}, status=201)




    
