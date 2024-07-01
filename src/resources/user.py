"""
This module contains the implementation of the User resource.

The User resource is responsible for handling the modifications,
deletions and retrievals of existing users.

Classes:
    UserResource: A resource class for seeing, modifying, and deleting existing users.
"""

from flask import Response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from .. import db
from ..decorators import require_user
from ..models import User
from .user_collection import is_valid_email


def validate_user_id(user_id):
    """
    Validate the user_id parameter.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        tuple: (bool, Response) A tuple containing a boolean indicating
        whether the user_id is valid and a Response object if invalid.
    """
    try:
        user_id = int(user_id)
        if user_id <= 0:
            return False, Response("Invalid user_id parameter", status=400)
    except ValueError:
        return False, Response("Invalid user_id parameter", status=400)
    return True, user_id


class UserId(Resource):
    """
    Resource class for seeing, modifying and deleting existing users. Implementing
    the User resource.

    This class handles the GET, PUT and DELETE requests for seeing,
    modifying and deleting existing users.


    Attributes:
        None

    Methods:
        get(user_id): Handle GET requests to retrieve information about a specific user.
        put(user_id): Handle PUT requests to update information about a specific user.
        delete(user_id): Handle DELETE requests to remove a specific user.
    """

    @require_user
    def get(self, api_key_user, user_id):
        """
        Handle GET requests to retrieve information about a specific user.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            Response: The response object containing user
            information and the appropriate status code.

        Retrieve a specific user's information
        ---
        tags:
            - User
        parameters:
            - in: path
              name: user_id
              schema:
                type: integer
                required: true
                description: The unique identifier of the user.
        responses:
            200:
              description: User information retrieved successfully
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      user_id:
                        type: integer
                        description: The unique identifier of the user
                      username:
                        type: string
                        description: The user's name
                      email:
                        type: string
                        description: The user's email address
            400:
              description: Bad Request - The user_id parameter is missing or invalid.
            401:
              description: Unauthorized -
              The provided api-key does not belong to the user_id provided.
            404:
              description: Not Found - No user exists with the specified user_id.

        """
        is_valid, response = validate_user_id(user_id)
        if not is_valid:
            return response

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response("User not found", status=404)
        # Check that the api-key corresponds to the user.
        if api_key_user.id != int(user_id):
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )

        user_data = user.serialize()
        return user_data, 200

    @require_user
    def put(self, api_key_user, user_id):
        """
        Handle PUT requests to update information about a specific user.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            Response: The response object containing
            the result of the update operation and the appropriate status code.

        Update a specific user's information
        ---
        tags:
          - User
        parameters:
            - in: path
              name: user_id
              schema:
                type: integer
                required: true
                description: The unique identifier of the user.
            - in: body
              name: body
              schema:
                id: User
                properties:
                  username:
                    type: string
                    description: The user's name
                  email:
                    type: string
                    description: The user's email
                oneOf:
                  - required: ['username']
                  - required: ['email']
        responses:
          200:
            description:
            User updated successfully.
          400:
            description:
            Bad Request - The user_id parameter is missing or invalid,
                        or no username or email provided.
          401:
            description:
            Unauthorized - The provided api-key does not belong to the user_id provided.
          404:
            description:
            Not Found - No user exists with the specified user_id.
          409:
            description:
            Conflict - The email provided is in an incorrect format
                        or the username already exists.
        """
        is_valid, response = validate_user_id(user_id)
        if not is_valid:
            return response

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response("User not found", status=404)
        # Check that the api-key corresponds to the user.
        if api_key_user.id != int(user_id):
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )
        data = request.get_json()
        if "username" in data:
            user.username = data["username"]

        if "email" in data:
            if not is_valid_email(data["email"]):
                return Response("Incorrect email format", status=409)
            user.email = data["email"]

        if "username" not in data and "email" not in data:
            return Response("No username or email provided", status=400)

        try:
            db.session.commit()
            return Response("User updated successfully", status=200)

        except IntegrityError:
            db.session.rollback()
            return Response("Username already exists", status=409)

    @require_user
    def delete(self, api_key_user, user_id):
        """
        Handle DELETE requests to remove a specific user.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            Response:
            The response object indicating the success or failure of the delete operation.

        Delete a specific user.
        ---
        tags:
          - User
        parameters:
          - in: path
            name: user_id
            schema:
              type: integer
              required: true
              description: The unique identifier of the user.
        responses:
          200:
            description: User deleted successfully.
          400:
            description: Bad Request - The user_id parameter is missing or invalid.
          401:
            description:
            Unauthorized - The provided api-key does not belong to the user_id provided.
          404:
            description: Not Found - No user exists with the specified user_id.
        """
        is_valid, response = validate_user_id(user_id)
        if not is_valid:
            return response

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response("User not found", status=404)

        # Check that the api-key corresponds to the user.
        if api_key_user.id != int(user_id):
            return Response(
                "The provided Api-key does not correspond to the user_id provided.",
                status=401,
            )

        db.session.delete(user)
        db.session.commit()
        return Response("User deleted successfully", status=200)
