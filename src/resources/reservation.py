from flask import Flask, request, Response
from flask_restful import Resource
from ..decorators import require_user
from datetime import datetime, date, timedelta

class GetReservations(Resource):
    @require_user
    def get(self, user):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else date.today()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.today() + timedelta(days=365)
        return [reservation.serialize() for reservation in user.reservations if start_date <= reservation.date <= end_date]