from flask import request, Response
from flask_restful import Resource
from ..decorators import require_user
from datetime import datetime, date, timedelta
from werkzeug.exceptions import UnsupportedMediaType
from ..models import Reservation
from src import db

class GetReservations(Resource):
    @require_user
    def get(self, user):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else date.today()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.today() + timedelta(days=365)
        return [reservation.serialize() for reservation in user.reservations if start_date <= reservation.start_time.date() <= end_date]

class CreateReservation(Resource):
    @require_user
    def post(self,user,room):
        if not request.is_json:
            raise UnsupportedMediaType()
        
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
        except Exception as e:
            return Response(f'Error parsing JSON data: {e}', status=400)
        
        date = data.get('date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')         
        
        if not date or not start_time or not end_time:
            return Response('Date, start_time and end_time are required', status=400)
        
        try:
            # Convert date, start_time, and end_time to datetime Python objects
            date = datetime.strptime(date, '%Y-%m-%d').date()
            start_time = datetime.combine(date, datetime.strptime(start_time, '%H:%M').time())
            end_time = datetime.combine(date, datetime.strptime(end_time, '%H:%M').time())
            if end_time.time() <= start_time.time(): # In case the reservation is on midnight
                end_time += timedelta(days=1)
                print("Terves")
        except ValueError:
            return Response('Invalid date or time format. Date format: YYYY-MM-DD. Time format: HH:MM', status=400)

        if start_time < datetime.now():
            return Response('Can not book past time slots', status=409)
        
        total_minutes = (end_time - start_time).total_seconds() // 60

        if total_minutes > room.max_time:
            return Response('Reservation is too long.', status=409)

        overlaping_reservations = Reservation.query.filter(
            (Reservation.room == room) & (
                ((Reservation.start_time >= start_time) & (Reservation.start_time <= end_time)) | # If a reservation starts in the timespan
                ((Reservation.end_time >= start_time) & (Reservation.end_time <= end_time)) | # If a reservation ends in the timespan
                ((Reservation.start_time <= start_time) & (Reservation.end_time >= end_time)) # If the whole timespan is already booked
            )).all()

        if overlaping_reservations:
            return Response('Time slot already taken', status=409)
        # Create and insert the object
        reservation = Reservation(room = room, user = user, start_time = start_time, end_time = end_time)
        db.session.add(reservation)
        db.session.commit()
        
        return Response("Reservation created successfully")
    
class DeleteReservation(Resource):
    @require_user
    def delete(self, user, room, reservation_id):
        reservation = Reservation.query.filter_by(id=reservation_id, user=user, room=room).first()
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return Response("Reservation deleted successfully", status=204)
        else:
            return Response("Reservation not found", status=404)