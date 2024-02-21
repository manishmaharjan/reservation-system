from flask import Flask, request, Response
from flask_restful import Api, Resource
from src import create_app, db
from src.models import ApiKey,Room,Reservation,User
from src.decorators import require_user, require_admin
app = create_app()

api = Api(app)

class GetReservations(Resource):
    @require_user
    def get(self, user):
        return [reservation.serialize() for reservation in user.reservations]


api.add_resource(GetReservations, "/api/reservations/")
