"""
Import modules
"""

import re
from json import JSONDecodeError

from flask import Response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import UnsupportedMediaType

from src import db

from ..models import ApiKey, User


class RegisterUser(Resource):
    """
    Resource class for registering a new user.

    This class handles the POST request for registering a new user. It expects JSON data
    containing the username and email of the user. It validates the data, creates a new
    User instance, generates an API key, and adds the user and API key to the database.

    Attributes:
        None

    Methods:
        post(self): Handles the POST request for registering a new user.

    """

    def post(self):
        """
        Handle POST requests to create a new user.

        Returns:
            Response: The response object with the appropriate status code and headers.
        """
        if not request.is_json:
            raise UnsupportedMediaType("Request must be in JSON format.")

        try:
            data = request.get_json(force=True)  # Try to parse JSON data
        except JSONDecodeError as e:
            return Response(f"Error parsing JSON data: {e}", status=400)

        username = data.get("username")
        email = data.get("email")

        # Check if username or email is missing
        if not username or not email:
            return Response("Username and email are required", status=400)

        # Check email format
        if not is_valid_email(email):
            return Response("Incorrect email format", status=409)

        user = User(username=username, email=email)
        token = ApiKey.create_token()
        api_key = ApiKey(key=ApiKey.key_hash(token), user=user)

        # Add instances to the database
        try:
            db.session.add(user)
            db.session.add(api_key)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return Response("Username already exists", status=409)

        return Response(headers={"api_key": token}, status=201)


def is_valid_email(email):
    """
    Check if the given email address is valid.

    Args:
        email (str): The email address to be validated.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    # Regular expression for validating email addresses
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Check if the email matches the regular expression pattern
    return re.match(email_regex, email) is not None
