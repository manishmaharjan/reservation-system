from flask import Flask, request, Response
from flask_restful import Api, Resource
from src import create_app, db
from .resources import reservation, user

app = create_app()

api = Api(app)

api.add_resource(user.RegisterUser, "/api/user/register/")
api.add_resource(reservation.GetReservations, "/api/reservations/")
