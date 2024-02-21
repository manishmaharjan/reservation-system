from flask import Flask, request, Response
from flask_restful import Resource
from werkzeug.exceptions import UnsupportedMediaType
from ..models import ApiKey,User
from sqlalchemy.exc import IntegrityError
import re
from src import db

class RegisterUser(Resource):
    def post(self):
        if not request.is_json:
            raise UnsupportedMediaType()
        
        try:
            data = request.get_json(force=True)  # Try to parse JSON data
        except Exception as e:
            return Response(f'Error parsing JSON data: {e}', status=400)
        
        username = data.get('username')
        email = data.get('email')

        # Check if username or email is missing
        if not username or not email:
            return Response('Username and email are required', status=400)

        user = User(username=username, email=email)
        token = ApiKey.create_token()
        api_key = ApiKey(key=ApiKey.key_hash(token), user = user)

        # Check email format
        if not is_valid_email(email):
            return Response('Incorrect email format', status=409)
        # Add instances to the database
        try:
            db.session.add(user)
            db.session.add(api_key)
            db.session.commit()
        except IntegrityError: 
            db.session.rollback()
            return Response('Username already exists', status=409)

        return Response(headers={'api_key': token}, status=201)

def is_valid_email(email):
    # Regular expression for validating email addresses
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Check if the email matches the regular expression pattern
    return re.match(email_regex, email) is not None

