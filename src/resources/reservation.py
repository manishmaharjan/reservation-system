from flask import Flask, request, Response, jsonify
from flask_restful import Resource
from ..decorators import require_user, require_admin
from datetime import datetime, date, timedelta
from werkzeug.exceptions import UnsupportedMediaType
from ..models import Reservation, db
from sqlalchemy import desc
class GetReservations(Resource):
    @require_user
    def get(self, user):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else date.today()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.today() + timedelta(days=365)
        return [reservation.serialize() for reservation in user.reservations if start_date <= reservation.date <= end_date]

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
            return Response('date, start_time and end_time are required', status=400)
        
        try:        
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response('Invalid date format. Date format should be YYYY-MM-DD')
        
        try:
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            return Response('Invalid time format. Time format should be HH:MM', status=400)
        
        # Check if any other reservation starts in the provided timespan
        Reservation.query.filter(Reservation.start_time> start_time,
                                 Reservation.start_time > end_time)
        # Check if any other reservation ends in the provided timespan
        Reservation.query.filter(Reservation.end> start_time,
                                 Reservation.end > end_time)
        lastReservation = Reservation.query.filter(Reservation.start_time < start_time).order_by(desc(Reservation.start_time)).first()
        
        if lastReservation.end_time > start_time:
            return Response('Time slot already taken', status=400)



class DeleteReservation(Resource):
    @require_user
    def delete(self, user, room, reservation_id):
#        reservation = Reservation.query.get(int(reservation_id))
        reservation = Reservation.query.filter_by(id=reservation_id, user=user, room=room).first()
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return jsonify({'message': 'Reservation deleted successfully'}), 204
        else:
            return jsonify({'error': 'Reservation not found'}), 404

class GetReservationList(Resource):
    @require_admin
    def get(self):
        reservations = Reservation.query.all()
        return jsonify([reservation.serialize() for reservation in reservations])
