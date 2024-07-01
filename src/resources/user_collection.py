"""
This module contains the implementation
of the UserCollection resource and related functions.

The UserCollection resource is responsible
 for handling the registration of new users. It provides
an endpoint for creating a new user by
accepting a JSON payload containing the username
and email, and another endpoint to get a list of all the users.
 The module also includes a helper function for validating email addresses.

Classes:
    UserCollection: A resource class for
    registering a new user and getting a list of all the users.

Functions:
    is_valid_email: Check if the given email address is valid.
"""

import re

from flask import Response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from .. import db
from ..decorators import require_admin, require_user
from ..models import ApiKey, User


class UserCollection(Resource):
    """
    Resource class for registering a new user or getting a list of all the users.

    This class handles the POST request for registering a new user. It expects JSON data
    containing the username and email of the user. It validates the data, creates a new
    User instance, generates an API key, and adds the user and API key to the database.
    It also handles a GET request which gets a list of all the users, and returns it.

    Attributes:
        None

    Methods:
        get(self): Handles the GET request for returning a list with all the users.
        post(self): Handles the POST request for registering a new user.

    """

    @require_admin
    def get(self):
        """
        Handle GET requests to retrieve a list of all users.

        Returns:
            Response: The response object with the appropriate status code and headers.

        Retrieve a list of all users. Requires an admin API key in the 'Api-key' header.
        ---
        tags:
          - User
        parameters:
          - in: header
            name: Api-key
            type: string
            required: true
            description: Api-key corresponding to an admin account.
        responses:
          200:
            description: List of all users retrieved successfully.
        """
        users = User.query.all()

        users_list = [user.serialize() for user in users]

        return users_list, 200

    def post(self):
        """
        Handle POST requests to create a new user.

        Returns:
            Response: The response object with the appropriate status code and headers.

        Create a new user
        ---
        tags:
          - User
        parameters:
          - in: body
            name: body
            schema:
              id: User
              required:
                - username
                - email
              properties:
                username:
                  type: string
                  description: The user's name
                email:
                  type: string
                  description: The user's email
        responses:
          201:
            description: User created successfully
            headers:
              api-key:
                description: The API key for the newly created user.
                schema:
                  type: string
              user_id:
                description: The id of the newly created user.
                schema:
                  type: integer
          400:
            description:
            Bad Request - The JSON data provided is malformed
            or missing required fields (email, username).
          409:
            description:
            Conflict - Conflict - The email provided is not in a
            valid format or the username already exists.
          415:
            description:
            Unsupported Media Type - The content type of
            the request is not supported. Ensure you are sending JSON data.

        """
        if not request.is_json:
            return Response("Request must be in JSON format.", status=415)

        try:
            data = request.get_json(force=True)  # Try to parse JSON data
            username = data.get("username")
            email = data.get("email")
        except:
            return Response(f"Error parsing JSON data", status=400)

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

        return Response(headers={"api_key": token, "user_id": user.id}, status=201)


@staticmethod
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
