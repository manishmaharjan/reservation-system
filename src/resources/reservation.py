"""

Import modules
"""

from datetime import datetime, date, timedelta
from json import JSONDecodeError
from flask_restful import Resource
from werkzeug.exceptions import UnsupportedMediaType
from flask import request, Response
from src import db
from ..models import Reservation
from ..decorators import require_user


class GetReservations(Resource):
    """
    Resource class for retrieving reservations for a user within a specified date range.
    """

    @require_user
    def get(self, user):
        """
        Get a list of reservations for a user within a specified date range.

        Args:
            user (User): The user object.

        Returns:
            list: A list of serialized reservation objects.
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
    Represents a resource for creating a new reservation for a user in a specified room.
    """

    @require_user
    def post(self, user, room):
        """
        Create a new reservation for a user in a specified room.

        Args:
            user (User): The user object.
            room (Room): The room object.

        Returns:
            Response: The response indicating the success or failure of the reservation creation.
        """
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
            # In case the reservation is on midnight
            if end_time.time() <= start_time.time():
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
                # If a reservation starts in the timespan
                (
                    (Reservation.start_time >= start_time)
                    & (Reservation.start_time <= end_time)
                )
                |
                # If a reservation ends in the timespan
                (
                    (Reservation.end_time >= start_time)
                    & (Reservation.end_time <= end_time)
                )
                |
                # If the whole timespan is already booked
                (
                    (Reservation.start_time <= start_time)
                    & (Reservation.end_time >= end_time)
                )
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
    Resource class for deleting a reservation for a user in a specified room.
    """

    class GetReservations(Resource):
        """
        Resource class for retrieving reservations for a user within a specified date range.
        """

        @require_user
        def get(self, user):
            """
            Get a list of reservations for a user within a specified date range.

            Args:
                user (User): The user object.

            Returns:
                list: A list of serialized reservation objects.
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
        Resource class for creating a new reservation for a user in a specified room.
        """

        @require_user
        def post(self, user, room):
            """
            Create a new reservation for a user in a specified room.

            Args:
                user (User): The user object.
                room (Room): The room object.

            Returns:
                Response:
                The response indicating the success or failure of the reservation creation.
            """
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
                return Response(
                    "Date, start_time and end_time are required", status=400
                )

            try:
                # Convert reservation_date, start_time, and end_time to datetime Python objects
                reservation_date = datetime.strptime(
                    reservation_date, "%Y-%m-%d"
                ).date()
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
        Resource class for deleting a reservation for a user in a specified room.
        """

        @require_user
        def delete(self, user, room, reservation_id):
            """
            Delete a reservation for a user in a specified room.

            Args:
                user (User): The user object.
                room (Room): The room object.
                reservation_id (int): The ID of the reservation to be deleted.

            Returns:
                Response: The response indicating the success
                or failure of the reservation deletion.
            """
            reservation = Reservation.query.filter_by(
                id=reservation_id, user=user, room=room
            ).first()
            if reservation:
                db.session.delete(reservation)
                db.session.commit()
                return Response("Reservation deleted successfully", status=204)
            return Response("Reservation not found", status=404)
