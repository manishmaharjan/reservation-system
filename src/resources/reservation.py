"""
This module contains the implementation of the Reservation resource.

The Reservation resource is responsible for handling the modifications,
deletions and retrievals of existing reservations.

Classes:
    ReservationId: A resource class for seeing, modifying and deleting existing reservations.
"""

from datetime import datetime, timedelta

from flask import Response, request
from flask_restful import Resource

from .. import db
from ..decorators import require_user
from ..models import Reservation, Room


def validate_user_id(user_id):
    """
    Validate the user ID.

    This method attempts to convert the provided user ID
    to an integer and checks if it's greater than 0.
    If the conversion fails or the user ID is not greater than 0,
    it returns an error response.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        Response: A response object with an error message and status code 400
        if the user ID is invalid. If the user ID is valid, it does not return anything.
    """
    try:
        user_id = int(user_id)
        if user_id <= 0:
            return Response("Invalid user_id parameter", status=400)
    except ValueError:
        return Response("Invalid user_id parameter", status=400)
    return user_id


def check_overlapping_reservations(room, start_time, end_time):
    """
    Check for overlapping reservations.

    Args:
        room (Room): The room for the reservation.
        start_time (datetime): The start time of the reservation.
        end_time (datetime): The end time of the reservation.

    Returns:
        Response: An error response if there are overlapping reservations, None otherwise.
    """
    overlapping_reservations = Reservation.query.filter(
        (Reservation.room == room)
        & (
            (
                (Reservation.start_time >= start_time)
                & (Reservation.start_time <= end_time)
            )
            | (
                (Reservation.end_time >= start_time)
                & (Reservation.end_time <= end_time)
            )
            | (
                (Reservation.start_time <= start_time)
                & (Reservation.end_time >= end_time)
            )
        )
    ).all()
    if overlapping_reservations:
        return Response("Time slot already taken", status=409)
    return None


def check_reservation_duration_and_overlap(room, start_time, end_time):
    """
    Check the duration of a reservation and if it overlaps with other reservations.

    This function calculates the total duration of a reservation
    in minutes and checks if it exceeds
    the maximum allowed time for the room. If it does, it returns
    a response indicating that the reservation
    is too long.

    It also checks if the reservation overlaps with any existing
    reservations for the room. If there is an overlap,
    it returns a response indicating that the time slot is already taken.

    If the reservation duration is within the allowed limit and
    there are no overlapping reservations, it returns None.

    Args:
        room (Room): The room for the reservation.
        start_time (datetime): The start time of the reservation.
        end_time (datetime): The end time of the reservation.

    Returns:
        Response: An error response if the reservation duration
        exceeds the room's max time or if there are overlapping reservations.
        None: If the reservation duration is within the allowed limit and there
        are no overlapping reservations.
    """
    total_minutes = (end_time - start_time).total_seconds() // 60
    if total_minutes > room.max_time:
        return Response("Reservation is too long.", status=409)

    # Check for overlapping reservations
    response = check_overlapping_reservations(room, start_time, end_time)
    if response:
        return response

    return None


class ReservationId(Resource):
    """
    Resource class for seeing, modifying and deleting existing reservations. Implementing
    the Reservation resource.

    This class handles the GET, PUT and DELETE requests for seeing,
    modifying and deleting existing reservations.


    Attributes:
        None

    Methods:
        get(user_id, reservation_id):
        Handle GET requests to retrieve information about a specific reservation.

        put(user_id, reservation_id):
        Handle PUT requests to update information about a specific reservation.

        delete(user_id, reservation_id):
        Handle DELETE requests to remove a specific reservation.
    """

    @require_user
    def get(self, api_key_user, user_id, reservation_id):
        """
        Retrieve a specific reservation for a given user.

        This method handles GET requests to retrieve a reservation for a specific user.
        The request must include a valid API key in the header,
        and the API key must correspond to the user_id provided.

        Args:
            api_key_user (User): The user associated with the provided API key.
            user_id (int): The unique identifier of the user.
            reservation_id (int): The unique identifier of the reservation.

        Returns:
            Response: The reservation details if the reservation belongs to the user,
            or an error message with the appropriate status code.

            ---
            tags:
              - Reservations
            parameters:
              - in: header
                name: Api-key
                type: string
                required: true
                description:
                The user for whom to retrieve the reservation using API key for authentication.
              - in: path
                name: user_id
                type: integer
                required: true
                description: The unique identifier of the user.
              - in: path
                name: reservation_id
                type: integer
                required: true
                description: The unique identifier of the reservation.
            responses:
              200:
                description: The reservation details.
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        user:
                          type: string
                          description: The username of the user.
                        room:
                          type: string
                          description: The name of the reserved room.
                        date:
                          type: string
                          format: date
                          description: The date of the reservation.
                        time-span:
                          type: string
                          description: The time span of the reservation.
                      example:
                        user: "john_doe"
                        room: "Conference Room 1"
                        date: "2023-05-28"
                        time-span: "10:00 - 11:00"
              400:
                description: Invalid user_id parameter.
              401:
                description: The provided API key does not correspond to the user_id provided.
              403:
                description: Reservation does not belong to the provided user_id.
              404:
                description: No reservation found with the provided reservation_id.
        """

        user_id = validate_user_id(user_id)
        if isinstance(user_id, Response):
            return user_id
        # Check that the api-key corresponds to the user.
        if api_key_user.id != user_id:
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )
        try:
            reservation_id = int(reservation_id)
            if reservation_id <= 0:
                return Response("Invalid reservation_id parameter", status=400)
        except ValueError:
            return Response("Invalid reservation_id parameter", status=400)

        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id=reservation_id).first()
        if not reservation:
            return Response(
                "No reservation found with the provided reservation_id.", status=404
            )
        if reservation.user_id != user_id:
            return Response(
                "Reservation does not belong to the provided user_id.", status=403
            )
        reservation_data = reservation.serialize()
        return reservation_data, 200

    @require_user
    def delete(self, api_key_user, user_id, reservation_id):
        """
        Delete a specific reservation for a given user.

        This method handles DELETE requests to remove a reservation for a specific user.
        The request must include a valid API key in the header,
        and the API key must correspond to the user_id provided.

        Args:
            api_key_user (User): The user associated with the provided API key.
            user_id (int): The unique identifier of the user.
            reservation_id (int): The unique identifier of the reservation.

        Returns:
            Response: A success message if the reservation is deleted,
            or an error message with the appropriate status code.

            ---
            tags:
            - Reservations
            parameters:
            - in: header
              name: Api-key
              type: string
              required: true
              description: T
              he user for whom to delete the reservation using API key for authentication.
            - in: path
              name: user_id
              type: integer
              required: true
              description: The unique identifier of the user.
            - in: path
              name: reservation_id
              type: integer
              required: true
              description: The unique identifier of the reservation.
            responses:
              200:
                description: Reservation deleted successfully.
                content:
                application/json:
                    schema:
                    type: object
                    properties:
                        message:
                        type: string
                        example: "Reservation deleted successfully"
              400:
                description: Invalid user_id parameter.
              401:
                description: The provided API key does not correspond to the user_id provided.
              403:
                description: Reservation does not belong to the provided user_id.
              404:
                description: No reservation found with the provided reservation_id.
        """

        user_id = validate_user_id(user_id)
        if isinstance(user_id, Response):
            return user_id

        # Check that the api-key corresponds to the user.
        if api_key_user.id != user_id:
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )

        # Check correct reservation_id
        try:
            reservation_id = int(reservation_id)
            if reservation_id <= 0:
                return Response("Invalid reservation_id parameter", status=400)
        except ValueError:
            return Response("Invalid reservation_id parameter", status=400)

        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id=reservation_id).first()
        if not reservation:
            return Response(
                "No reservation found with the provided reservation_id.", status=404
            )
        if reservation.user_id != user_id:
            return Response(
                "Reservation does not belong to the provided user_id.", status=403
            )

        # Delete the reservation
        db.session.delete(reservation)
        db.session.commit()
        return Response("Reservation deleted successfully", status=200)

    @require_user
    def put(self, api_key_user, user_id, reservation_id):
        """
        Update a specific reservation for a given user.

        This method handles PUT requests to update a reservation for a specific user.
        The request must include a valid API key in the header,
        and the API key must correspond to the user_id provided.
        The request body should be in JSON format and
        may include the new date, start-time, end-time, and room_id.

        Args:
            api_key_user (User): The user associated with the provided API key.
            user_id (int): The unique identifier of the user.
            reservation_id (int): The unique identifier of the reservation.

        Returns:
            Response: A success message if the reservation is updated, or
            an error message with the appropriate status code.

            ---
            tags:
            - Reservations
            parameters:
            - in: header
              name: Api-key
              type: string
              required: true
              description:
              The user for whom to update the reservation using API key for authentication.
            - in: path
              name: user_id
              type: integer
              required: true
              description: The unique identifier of the user.
            - in: path
              name: reservation_id
              type: integer
              required: true
              description: The unique identifier of the reservation.
            - in: body
              name: body
              required: true
              description: The new details of the reservation.
              schema:
                id: Reservation
                type: object
                properties:
                    date:
                      type: string
                      format: date
                      description: The new date of the reservation.
                    start-time:
                      type: string
                      format: time
                      description: The new start time of the reservation.
                    end-time:
                      type: string
                      format: time
                      description: The new end time of the reservation.
                    roomId:
                      type: integer
                      description: The new room id for the reservation.
                example:
                    date: "2024-06-01"
                    start-time: "14:00"
                    end-time: "16:00"
                    room-id: 2
            responses:
              200:
                description: Reservation updated successfully.
              400:
                description: Invalid user_id parameter or invalid input data.
              401:
                description: The provided API key does not correspond to the user_id provided.
              403:
                description: Reservation does not belong to the provided user_id.
              404:
                description:
                No reservation found with the provided reservation_id
                or no room found with the provided room id.
              409:
                description:
                The new time slot is already taken or the
                reservation duration exceeds the room's max time.
        """
        user_id = validate_user_id(user_id)
        if isinstance(user_id, Response):
            return user_id

        # Check that the api-key corresponds to the user.
        if api_key_user.id != user_id:
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )
        # Update reservation details
        try:
            reservation_id = int(reservation_id)
            if reservation_id <= 0:
                return Response("Invalid reservation_id parameter", status=400)
        except ValueError:
            return Response("Invalid reservation_id parameter", status=400)

        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id=reservation_id).first()
        if not reservation:
            return Response(
                "No reservation found with the provided reservation_id.", status=404
            )
        if reservation.user_id != user_id:
            return Response(
                "Reservation does not belong to the provided user_id.", status=403
            )

        # Ensure correct json
        if not request.is_json:
            return Response("Request must be in JSON format.", status=415)
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
            reservation_date = data.get("date")
            start_time = data.get("start-time")
            end_time = data.get("end-time")
            room_id = data.get("roomId")
        except:
            return Response(f"Error parsing JSON data", status=400)

        if not reservation_date and not start_time and not end_time and not room_id:
            return Response(
                "At least one of date, start-time, end-time, or roomId is required.",
                status=400,
            )

        if room_id:
            room = Room.query.filter_by(id=room_id).first()
            if not room:
                return Response("No room found with the provided room id.", status=404)
        else:
            room = reservation.room

        # Update reservation details
        try:
            if reservation_date:
                reservation_date = datetime.strptime(
                    reservation_date, "%Y-%m-%d"
                ).date()
            else:
                reservation_date = reservation.start_time.date()

            if start_time:
                start_time = datetime.combine(
                    reservation_date, datetime.strptime(start_time, "%H:%M").time()
                )
            else:
                start_time = datetime.combine(
                    reservation_date, reservation.start_time.time()
                )

            if end_time:
                end_time = datetime.combine(
                    reservation_date, datetime.strptime(end_time, "%H:%M").time()
                )
                if end_time.time() <= start_time.time():
                    end_time += timedelta(days=1)
            else:
                end_time = datetime.combine(
                    reservation_date, reservation.end_time.time()
                )
        except:
            return Response(
                "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM",
                status=400,
            )

        response = check_reservation_duration_and_overlap(room, start_time, end_time)
        if response:
            return response

        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.room = room

        db.session.commit()

        return Response("Reservation updated successfully", status=200)
