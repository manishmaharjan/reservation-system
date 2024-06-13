"""
This module contains the implementation of the User resource.

The User resource is responsible for handling the modifications, deletions and retrievals of existing users.

Classes:
    UserId: A resource class for seeing, modifying and deleting existing users.

"""

import re
from json import JSONDecodeError

from flask import Response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import UnsupportedMediaType

from src import db
from src.resources.userCollection import is_valid_email

from ..models import ApiKey, User

class UserId(Resource):
    """
    Resource class for seeing, modifying and deleting existing users. Implementing
    the User resource.

    This class handles the GET, PUT and DELETE requests for seeing, modifying and deleting existing users. 
    

    Attributes:
        None

    Methods:
        get(userId): Handle GET requests to retrieve information about a specific user.
        put(userId): Handle PUT requests to update information about a specific user.
        delete(userId): Handle DELETE requests to remove a specific user.
    """
    def get(self, userId):
        """
        Handle GET requests to retrieve information about a specific user.

        Args:
            userId (int): The unique identifier of the user.

        Returns:
            Response: The response object containing user information and the appropriate status code.
        
        Retrieve a specific user's information
        ---
        tags:
            - User
        parameters:
            - in: path
              name: userId
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
                      userId:
                        type: integer
                        description: The unique identifier of the user
                      username:
                        type: string
                        description: The user's name
                      email:
                        type: string
                        description: The user's email address
            400:
              description: Bad Request - The userId parameter is missing or invalid.
            404:
              description: Not Found - No user exists with the specified userId.

        """
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status = 400)
        except ValueError:
            return Response("Invalid userId parameter", status = 400)

        user = User.query.filter_by(id = userId).first()
        if user is None:
            return Response("User not found", status = 404)

        user_data = user.serialize()
        return user_data, 200

    def put(self, userId):
        """
        Handle PUT requests to update information about a specific user.

        Args:
            userId (int): The unique identifier of the user.

        Returns:
            Response: The response object containing the result of the update operation and the appropriate status code.
        
        Update a specific user's information
        ---
        tags:
          - User
        parameters:
            - in: path
              name: userId
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
            description: User updated successfully.
          400:
            description: Bad Request - The userId parameter is missing or invalid, or no username or email provided.
          404:
            description: Not Found - No user exists with the specified userId.
          409:
            description: Conflict - The email provided is in an incorrect format or the username already exists.
        """
        try:
            try:
                userId = int(userId)
                if userId <= 0:
                    return Response("Invalid userId parameter", status = 400)
            except ValueError:
                return Response("Invalid userId parameter", status = 400)

            user = User.query.filter_by(id = userId).first()
            if user is None:
                return Response("User not found", status= 404)

            data = request.get_json()
            if 'username' in data:
                user.username = data['username']
            
            if 'email' in data:
                if not is_valid_email(data['email']):
                    return Response("Incorrect email format", status=409)
                user.email = data['email']
            
            if 'username' not in data and 'email' not in data:
                return Response("No username or email provided", status = 400)
            
            db.session.commit()
            return Response("User updated successfully", status = 200)

        except IntegrityError:
            db.session.rollback()
            return Response("Username already exists", status=409)
    

    def delete(self, userId):
        """
        Handle DELETE requests to remove a specific user.

        Args:
            userId (int): The unique identifier of the user.

        Returns:
            Response: The response object indicating the success or failure of the delete operation.
        
        Delete a specific user.
        ---
        tags:
          - User
        parameters:
          - in: path
            name: userId
            schema:
              type: integer
              required: true
              description: The unique identifier of the user.
        responses:  
          200:
            description: User deleted successfully.
          400:
            description: Bad Request - The userId parameter is missing or invalid.
          404:
            description: Not Found - No user exists with the specified userId.
        """
        try:
            userId = int(userId)
            if userId <= 0:
                return Response("Invalid userId parameter", status = 400)
        except ValueError:
            return Response("Invalid userId parameter", status = 400)

        user = User.query.filter_by(id = userId).first()
        if user is None:
            return Response("User not found", status= 404)

        db.session.delete(user)
        db.session.commit()
        return Response("User deleted successfully", status = 200)
