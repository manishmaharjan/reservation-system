"""
This module contains the implementation of the Reservation resource.

The Reservation resource is responsible for handling the modifications, deletions and retrievals of existing reservations.

Classes:
    ReservationId: A resource class for seeing, modifying and deleting existing reservations.
"""

from flask import Response, request
from flask_restful import Resource
from json import JSONDecodeError
from datetime import date, datetime, timedelta

from src import db
from ..decorators import require_user
from ..models import Reservation, Room

class ReservationId(Resource):
    """
    Resource class for seeing, modifying and deleting existing reservations. Implementing
    the Reservation resource.

    This class handles the GET, PUT and DELETE requests for seeing, modifying and deleting existing reservations. 
    

    Attributes:
        None

    Methods:
        get(userId, reservationId): Handle GET requests to retrieve information about a specific reservation.
        put(userId, reservationId): Handle PUT requests to update information about a specific reservation.
        delete(userId, reservationId): Handle DELETE requests to remove a specific reservation.
    """
    @require_user
    def get(self,apiKeyUser, userId, reservationId):
        """
        Retrieve a specific reservation for a given user.

        This method handles GET requests to retrieve a reservation for a specific user.
        The request must include a valid API key in the header, and the API key must correspond to the userId provided.

        Args:
            apiKeyUser (User): The user associated with the provided API key.
            userId (int): The unique identifier of the user.
            reservationId (int): The unique identifier of the reservation.

        Returns:
            Response: The reservation details if the reservation belongs to the user, or an error message with the appropriate status code.

            ---
            tags:
              - Reservations
            parameters:
              - in: header
                name: Api-key
                type: string
                required: true
                description: The user for whom to retrieve the reservation using API key for authentication.
              - in: path
                name: userId
                type: integer
                required: true
                description: The unique identifier of the user.
              - in: path
                name: reservationId
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
                description: Invalid userId parameter.
              401:
                description: The provided API key does not correspond to the userId provided.
              403:
                description: Reservation does not belong to the provided userId.
              404:
                description: No reservation found with the provided reservationId.
        """
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status = 400)
        except ValueError:
            return Response("Invalid userId parameter", status = 400)      

        # Check that the api-key corresponds to the user.
        if apiKeyUser.id != userId:
            return Response("The provided Api-key does not correspond to the userId provided.", status = 401)
        
        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id = reservationId).first()
        if not reservation:
            return Response("No reservation found with the provided reservationId.", status = 404)
        if reservation.user_id != userId:
            return Response("Reservation does not belong to the provided userId.", status = 403)
        reservation_data = reservation.serialize()
        return reservation_data, 200
    @require_user
    def delete(self, apiKeyUser, userId, reservationId):
        """
        Delete a specific reservation for a given user.

        This method handles DELETE requests to remove a reservation for a specific user.
        The request must include a valid API key in the header, and the API key must correspond to the userId provided.

        Args:
            apiKeyUser (User): The user associated with the provided API key.
            userId (int): The unique identifier of the user.
            reservationId (int): The unique identifier of the reservation.

        Returns:
            Response: A success message if the reservation is deleted, or an error message with the appropriate status code.

            ---
            tags:
            - Reservations
            parameters:
            - in: header
              name: Api-key
              type: string
              required: true
              description: The user for whom to delete the reservation using API key for authentication.
            - in: path
              name: userId
              type: integer
              required: true
              description: The unique identifier of the user.
            - in: path
              name: reservationId
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
                description: Invalid userId parameter.
              401:
                description: The provided API key does not correspond to the userId provided.
              403:
                description: Reservation does not belong to the provided userId.
              404:
                description: No reservation found with the provided reservationId.
        """
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status=400)
        except ValueError:
            return Response("Invalid userId parameter", status=400)

        # Check that the api-key corresponds to the user.
        if (apiKeyUser.id != userId):
            return Response("The provided Api-key does not correspond to the userId provided.", status=401)

        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id=reservationId).first()
        if not reservation:
            return Response("No reservation found with the provided reservationId.", status=404)
        if reservation.user_id != userId:
            return Response("Reservation does not belong to the provided userId.", status=403)

        # Delete the reservation
        db.session.delete(reservation)
        db.session.commit()
        return Response("Reservation deleted successfully", status=200)
    
    @require_user
    def put(self, apiKeyUser, userId, reservationId):
        """
        Update a specific reservation for a given user.

        This method handles PUT requests to update a reservation for a specific user.
        The request must include a valid API key in the header, and the API key must correspond to the userId provided.
        The request body should be in JSON format and may include the new date, start-time, end-time, and room_id.

        Args:
            apiKeyUser (User): The user associated with the provided API key.
            userId (int): The unique identifier of the user.
            reservationId (int): The unique identifier of the reservation.

        Returns:
            Response: A success message if the reservation is updated, or an error message with the appropriate status code.

            ---
            tags:
            - Reservations
            parameters:
            - in: header
              name: Api-key
              type: string
              required: true
              description: The user for whom to update the reservation using API key for authentication.
            - in: path
              name: userId
              type: integer
              required: true
              description: The unique identifier of the user.
            - in: path
              name: reservationId
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
                description: Invalid userId parameter or invalid input data.
              401:
                description: The provided API key does not correspond to the userId provided.
              403:
                description: Reservation does not belong to the provided userId.
              404:
                description: No reservation found with the provided reservationId or no room found with the provided room id.
              409:
                description: The new time slot is already taken or the reservation duration exceeds the room's max time.
        """
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status=400)
        except ValueError:
            return Response("Invalid userId parameter", status=400)

        # Check that the api-key corresponds to the user.
        if apiKeyUser.id != userId:
            return Response("The provided Api-key does not correspond to the userId provided.", status=401)

        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id=reservationId).first()
        if not reservation:
            return Response("No reservation found with the provided reservationId.", status=404)
        if reservation.user_id != userId:
            return Response("Reservation does not belong to the provided userId.", status=403)

        # Ensure correct json
        if not request.is_json:
            return Response("Request must be in JSON format.", status=415)
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
            reservation_date = data.get("date")
            start_time = data.get("start-time")
            end_time = data.get("end-time")
            room_id = data.get("roomId")
        except JSONDecodeError as e:
            return Response(f"Error parsing JSON data", status=400)

        if not reservation_date and not start_time and not end_time and not room_id:
            return Response("At least one of date, start-time, end-time, or roomId is required.", status=400)

        if room_id:
            room = Room.query.filter_by(id=room_id).first()
            if not room:
                return Response("No room found with the provided room id.", status=404)
        else:
            room = reservation.room

        # Update reservation details
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status=400)
        except ValueError:
            return Response("Invalid userId parameter", status=400)

        # Check that the api-key corresponds to the user.
        if (apiKeyUser.id != userId):
            return Response("The provided Api-key does not correspond to the userId provided.", status=401)

        # Check that the reservation exists
        reservation = Reservation.query.filter_by(id=reservationId).first()
        if not reservation:
            return Response("No reservation found with the provided reservationId.", status=404)
        if reservation.user_id != userId:
            return Response("Reservation does not belong to the provided userId.", status=403)

        # Ensure correct json
        if not request.is_json:
            return Response("Request must be in JSON format.", status=415)
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
            reservation_date = data.get("date")
            start_time = data.get("start-time")
            end_time = data.get("end-time")
            room_id = data.get("roomId")
        except JSONDecodeError as e:
            return Response(f"Error parsing JSON data", status=400)

        if not reservation_date and not start_time and not end_time and not room_id:
            return Response("At least one of date, start-time, end-time, or roomId is required.", status=400)

        if room_id:
            room = Room.query.filter_by(id=room_id).first()
            if not room:
                return Response("No room found with the provided roomId.", status=404)
        else:
            room = reservation.room

        # Update reservation details
        try:
            if reservation_date:
                reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
            else:
                reservation_date = reservation.start_time.date()

            if start_time:
                start_time = datetime.combine(reservation_date, datetime.strptime(start_time, "%H:%M").time())
            else:
                start_time = datetime.combine(reservation_date, reservation.start_time.time())

            if end_time:
                end_time = datetime.combine(reservation_date, datetime.strptime(end_time, "%H:%M").time())
                if end_time.time() <= start_time.time():
                    end_time += timedelta(days=1)
            else:
                end_time = datetime.combine(reservation_date, reservation.end_time.time())
        except ValueError:
            return Response("Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM", status=400)

        total_minutes = (end_time - start_time).total_seconds() // 60
        if total_minutes > room.max_time:
            return Response("Reservation is too long.", status=409)

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
            & (Reservation.id != reservation.id)
        ).all()

        if overlapping_reservations:
            return Response("Time slot already taken", status=409)

        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.room = room

        db.session.commit()

        return Response("Reservation updated successfully", status=200)