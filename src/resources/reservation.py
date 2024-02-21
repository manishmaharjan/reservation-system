from flask import Flask, request, Response
from flask_restful import Resource
from ..decorators import require_user

class GetReservations(Resource):
    @require_user
    def get(self, user):
        return [reservation.serialize() for reservation in user.reservations]