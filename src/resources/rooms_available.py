"""
This module contains the implementation of the
RoomsAvailable resource, as well as a helper function.

The RoomsAvailable resource is responsible for
checking for available rooms in the specified date and time, with
the specified duration. It also includes a helper
function which checks if a room is available in a timespan.

Classes:
    RoomsAvailable: A resource class checking and returning
    the available rooms in th especified date and time with the specified duration.

Functions:
    is_room_available: Helper function which
     returns if a room is available in a specific timespan.
"""

from datetime import datetime, timedelta

from flask import Response, request
from flask_restful import Resource

from ..models import Room


class RoomsAvailable(Resource):
    """
    Resource class for handling availability of
    rooms based on date, time and duration.

    This class handles the GET request
    to check the availability of a room.

    Attrubutes:
        None

    Methods:
        get(self): Handle GET request to retrieve
        available rooms based on date, time and duration.
    """

    def get(self):
        """
        Retrieve available rooms based on the date,
        time and desired duration of the reservation.

        This method handles GET requests to retrieve information about available rooms.
        Having the date and time, it checks the
        availability of all the rooms in the database in that specific timespan,
        returning a list of all the available rooms. A duration parameter is optional,
        and if it is not inputed, the maximun time of the
        room will be taken as the desired duration of the reservation.

        Returns:
            Response: JSON response with available
            rooms or an empty list if no rooms are available.
        ---
        tags:
          - Rooms
        parameters:
          - in: query
            name: date
            required: true
            schema:
              type: string
              format: date
              example: "2024-06-30"
            description: The date for checking room availability (YYYY-MM-DD format)
          - in: query
            name: time
            required: true
            schema:
              type: string
              format: time
              example: "14:00"
            description: The time for checking room availability (HH:MM format)
          - in: query
            name: duration
            required: false
            schema:
              type: integer
              example: 120
            description: Optional duration of the reservation in minutes
        responses:
          200:
            description: List of available rooms retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    date:
                      type: string
                      example: "2024-06-30"
                      description: The date used for availability check
                    time:
                      type: string
                      example: "14:00"
                      description: The time used for availability check
                    available_rooms:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                            description: The id of the room.
                          room_name:
                            type: string
                            description: The name of the room.
                          capacity:
                            type: integer
                            description: The people capacity of the room.
                          max_time:
                            type: integer
                            description: The longest possible reservation in minutes.
                        example:
                          id: 4
                          room_name: "Conference room 1"
                          capacity: 9
                          max_time: 120
          400:
            description:
            Bad Request - Invalid date, time, or duration parameter provided.
        """

        # Parse query parameters
        date = request.args.get("date")
        time = request.args.get("time")
        duration = request.args.get("duration")

        if not date or not time:
            return Response("date and time parameters are required.", status=400)

        try:
            search_datetime = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
        except:
            return Response(
                "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time.",
                status=400,
            )

        if duration:
            try:
                duration = int(duration)
                if duration <= 0:
                    return Response("Duration must be a positive integer.", status=400)
            except ValueError:
                return Response("Duration must be a positive integer.", status=400)

        # Query all rooms
        rooms = Room.query.all()

        # List to store available rooms
        available_rooms = []

        # Check availability for each room
        for room in rooms:
            if is_room_available(room, search_datetime, duration):
                available_rooms.append(room.serialize())

        # Example response format
        response_data = {"date": date, "time": time, "available_rooms": available_rooms}

        return response_data, 200


def is_room_available(room, start_datetime, duration):
    """
    Check if the room is available within the specified datetime range.

    Args:
        room (Room): The room object to check availability for.
        start_datetime (datetime): Start datetime of the availability check.
        end_datetime (datetime): End datetime of the availability check.

    Returns:
        bool: True if the room is available, False otherwise.
    """
    # If duration is inputed duration, the max time otherwise.
    if not duration:
        end_datetime = start_datetime + timedelta(minutes=room.max_time)
    else:
        if duration > room.max_time:
            return False
        end_datetime = start_datetime + timedelta(minutes=duration)

    # Check if there are any reservations
    # that overlap with the specified datetime range
    for reservation in room.reservations:
        if (
            reservation.start_time < end_datetime
            and reservation.end_time > start_datetime
        ):
            return False

    return True
