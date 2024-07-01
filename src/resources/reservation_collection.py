"""
This module contains the implementation
of the ReservationCollection resource.

The ReservationCollection resource is responsible for
handling the creation of new reservations. It provides
an endpoint for creating a new reservation by accepting
a JSON payload containing the date, time and the id of the room
that will be booked. With another endpoint
to get a list of all the users.

Classes:
    ReservationCollection:
    A resource class for creating new reservations and
    getting a list of all reservations of the user.

"""

from datetime import datetime, timedelta

from flask import Response, request
from flask_restful import Resource
from .reservation import (
    check_overlapping_reservations,
    check_reservation_duration_and_overlap,
    validate_user_id,
)

from .. import db
from ..decorators import require_user
from ..models import Reservation, Room


class ReservationCollection(Resource):
    """
    Resource class for creating a new reservation or getting a
    list of all the reservations of a user.

    This class handles the POST request for creating a new reservation.
    It expects JSON data containing the date, time and id of the room.
    It checks that there is no other reservation
    at that time and date in that room, and then creates the reservation object.
    It also handles a GET request which gets a list
    of all the reservations of the user, and returns it.

    Attributes:
        None

    Methods:
        get(user_id): Handles the GET request for returning
        a list with all the reservations of the user.
        post(user_id): Handles the POST request for
        registering a new user.

    """

    def check_api_key_user(self, api_key_user, user_id):
        """
        Check that the api-key corresponds to the user.

        Args:
            api_key_user (User): The user associated with the provided API key.
            user_id (int): The unique identifier of the user.

        Returns:
            Response: An error response if the API key does not match the user_id, None otherwise.
        """
        if api_key_user.id != int(user_id):
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )
        return None

    def validate_and_parse_json(self):
        """
        Ensure the request body is in JSON format and parse the JSON data.

        Returns:
            tuple: Parsed JSON data and an error response if the JSON is invalid.
        """
        if not request.is_json:
            return None, Response("Request must be in JSON format.", status=415)
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
            return data, None
        except:
            return None, Response("Error parsing JSON data", status=400)

    @require_user
    def get(self, api_key_user, user_id):
        """
        Retrieve all reservations for a given user.

        This method handles GET requests to retrieve all
        reservations associated with a specific user.
        The request must include a valid API key in the header,
        and the API key must correspond to the user_id provided.

        Args:
            user_id (int): The unique identifier of the user for
            whom reservations are being retrieved.

        Returns:
            Response: A list of all reservations for the specified user,
            or an error message with the appropriate status code.

        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: Api-key
            type: string
            required: true
            description: The user for whom to retrieve
            reservations using API key for authentication.
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
                        description:
                        The username of the user who made the reservation.
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
            description: Invalid user_id parameter.
          401:
            description: The provided API key
            does not correspond to the user_id provided.
        """

        # Validate user_id parameter
        response = validate_user_id(user_id)
        if not isinstance(response, int):
            return response

        # Check that the API key corresponds to the user
        response = self.check_api_key_user(api_key_user, user_id)
        if response:
            return response

        reservation_list = [r.serialize() for r in api_key_user.reservations]

        return reservation_list, 200

    @require_user
    def post(self, api_key_user, user_id):
        """
        Create a new reservation for a given user.

        This method handles POST requests to create
        a new reservation for a specific user.
        The request must include a valid API key in the header,
        and the API key must correspond to the user_id provided.
        The reservation details (date, start-time, end-time,
        roomId) must be provided in the request body in JSON format.

        Args:
            api_key_user (User): The user associated
            with the provided API key.
            user_id (int): The unique identifier of the
            user for whom the reservation is being created.

        Returns:
            Response: A success message with status 201
            if the reservation is created successfully,
                    or an error message with the appropriate status code.

        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: Api-key
            type: string
            required: true
            description: The user for whom to
            create a reservation using API key for authentication.
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
            description: Invalid user_id parameter,
            or missing/invalid reservation details.
          401:
            description: The provided API key
            does not correspond to the user_id provided.
          404:
            description: No room found with the roomId provided.
          409:
            description: Reservation conflict
            (e.g., past time slot, overlapping reservation, reservation too long).
          415:
            description: The request body must be in JSON format.
        """

        # Validate user_id parameter
        response = validate_user_id(user_id)
        if not isinstance(response, int):
            return response

        # Check that the API key corresponds to the user
        response = self.check_api_key_user(api_key_user, user_id)
        if response:
            return response

        # Ensure the request body is in JSON format and parse the JSON data
        data, response = self.validate_and_parse_json()
        if response:
            return response

        # Extract reservation details from parsed data
        try:
          reservation_date = data.get("date")
          start_time = data.get("start-time")
          end_time = data.get("end-time")
          room_id = data.get("roomId")
        except:
          return Response("Error parsing JSON data", status=400)

        if not reservation_date or not start_time or not end_time or not room_id:
            return Response(
                "date, start-time, end-time and roomId are required", status=400
            )

        # Check that the room ID corresponds to a room
        room = Room.query.filter_by(id=room_id).first()
        if not room:
            return Response("No room found with the provided room id.", status=404)

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
        except Exception:
            return Response(
                "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM",
                status=400,
            )

        if start_time < datetime.now():
            return Response("Cannot book past time slots", status=409)

        response = check_reservation_duration_and_overlap(room, start_time, end_time)
        if response:
            return response

        # Check for overlapping reservations
        response = check_overlapping_reservations(room, start_time, end_time)
        if response:
            return response

        # Create and insert the reservation object
        reservation = Reservation(
            room=room, user=api_key_user, start_time=start_time, end_time=end_time
        )
        db.session.add(reservation)
        db.session.commit()

        return Response(
            "Reservation created successfully",
            headers={"reservation_id": reservation.id},
            status=201,
        )
