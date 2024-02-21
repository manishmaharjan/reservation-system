from http.client import FORBIDDEN
from flask import Flask, request, Response
from flask_restful import Api, Resource
from src import create_app, db
from src.models import *
from functools import wraps

app = create_app()

api = Api(app)

# Function to verify if the request comes from an admin righted user
def require_admin(func):
    def wrapper(*args, **kwargs):
        # The token will go in a special header named: "Api-key"
        key_hash = ApiKey.key_hash(request.headers.get("Api-key").strip())
        db_key = ApiKey.query.filter_by(key=key_hash).first()
        if db_key and db_key.admin:
            return func(db.key.user, *args, **kwargs)
        raise FORBIDDEN
    return wrapper

# Function to verify if the request comes from an actual user
def require_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # The token will go in a special header named: "Api-key"
        key_hash = ApiKey.key_hash(request.headers.get("Api-key").strip())
        db_key = ApiKey.query.filter_by(key= key_hash).first()
        if db_key:
            kwargs['user'] = db_key.user
            return func(*args, **kwargs)
        raise FORBIDDEN
    return wrapper

class GetReservations(Resource):
    @require_user
    def get(self, user):
        return [reservation.serialize() for reservation in user.reservations]


api.add_resource(GetReservations, "/api/reservations/")
