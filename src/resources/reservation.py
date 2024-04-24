"""
This module contains the resource classes for managing reservations in the reservation system.

It includes the following classes:

- GetReservations:
A resource class for retrieving reservations for a user within a specified date range.

- CreateReservation:
A resource class for creating a new reservation for a user in a specified room.

- DeleteReservation:
A resource class for deleting a reservation for a user in a specified room.
"""

from datetime import date, datetime, timedelta
from json import JSONDecodeError

from flask import Response, request
from flask_restful import Resource
from werkzeug.exceptions import UnsupportedMediaType

from src import db # type: ignore

from ..decorators import require_user
from ..models import Reservation


class GetReservations(Resource):
    """
    Represents a resource for retrieving reservations.

    This class provides a GET method that retrieves reservations
     based on the specified start and end dates.
    """

    @require_user
    def get(self, user):
        """
        Retrieves all reservations for a given user.
        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: API-KEY
            type: string
            required: true
            description: The user for whom to retrieve reservations using API key for authentication
        responses:
          200:
            description: A list of all reservations for the specified user.
        """
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        start_date = (
            datetime.strptime(start_date, "%Y-%m-%d").date()
            if start_date
            else date.today()
        )
        end_date = (
            datetime.strptime(end_date, "%Y-%m-%d").date()
            if end_date
            else date.today() + timedelta(days=365)
        )
        return [
            reservation.serialize()
            for reservation in user.reservations
            if start_date <= reservation.start_time.date() <= end_date
        ]


class CreateReservation(Resource):
    """
    Represents a resource for creating a reservation.

    Methods:
    - post: Handles the HTTP POST request for creating a reservation.
    """

    @require_user
    def post(self, user, room):
        """
        Create a new reservation for a given user and room.
        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: API-KEY
            type: string
            required: true
            description: The user for whom to retrieve reservations using API key for authentication
          - in: path
            name: room
            type: string
            required: true
            description: The room for the reservation.
          - in: body
            name: body
            schema:
              id: Reservation
              required:
                - date
                - start_time
                - end_time
              properties:
                date:
                  type: string
                  format: date
                  description: The date for the reservation.
                start_time:
                  type: string
                  format: time
                  description: The start time for the reservation.
                end_time:
                  type: string
                  format: time
                  description: The end time for the reservation.
        responses:
          200:
            description: Reservation created
        """
        # Code for creating a reservation
        if not request.is_json:
            raise UnsupportedMediaType()
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
        except JSONDecodeError as e:
            return Response(f"Error parsing JSON data: {e}", status=400)

        reservation_date = data.get("date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not reservation_date or not start_time or not end_time:
            return Response("Date, start_time and end_time are required", status=400)
        try:
            # Convert reservation_date, start_time, and end_time to datetime Python objects
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
                print("Terves")
        except ValueError:
            return Response(
                "Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM",
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
            room=room, user=user, start_time=start_time, end_time=end_time
        )
        db.session.add(reservation)
        db.session.commit()

        return Response("Reservation created successfully", status=209)


class DeleteReservation(Resource):
    """
    Represents a resource for deleting a reservation.

    This resource allows authenticated users to delete their own reservations for a specific room.

    Args:
        user (User): The authenticated user making the request.
        room (Room): The room for which the reservation is being deleted.
        reservation_id (int): The ID of the reservation to be deleted.

    Returns:
        Response: A response indicating the status of the deletion operation.

    Raises:
        None

    """

    @require_user
    def delete(self, user, room, reservation_id):
        """
        Delete a reservation for a given user, room, and reservation ID.
        ---
        tags:
          - Reservations
        parameters:
          - in: header
            name: API-KEY
            type: string
            required: true
            description: The user for whom to retrieve reservations using API key for authentication
          - in: path
            name: room
            type: string
            required: true
            description: The room for the reservation.
          - in: path
            name: reservation_id
            type: integer
            required: true
            description: The ID of the reservation.
        responses:
          200:
            description: Reservation deleted
        """
        reservation = Reservation.query.filter_by(
            id=reservation_id, user=user, room=room
        ).first()
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return Response("Reservation deleted successfully", status=204)
        return Response("Reservation not found", status=404)
