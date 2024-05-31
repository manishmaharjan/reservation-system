"""
This module contains the implementation of the User resource..

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
        """
        try:
            user = User.query.filter_by(id = userId).first()
            if user is None:
                return {"message": "User not found"}, 404

            user_data = user.serialize()
            return user_data, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def put(self, userId):
        """
        Handle PUT requests to update information about a specific user.

        Args:
            userId (int): The unique identifier of the user.

        Returns:
            Response: The response object indicating the success or failure of the update operation.
        """
        try:
            user = User.query.filter_by(id = userId).first()
            if user is None:
                return {"message": "User not found"}, 404

            data = request.get_json()
            if 'username' in data:
                user.username = data['username']
            
            if 'email' in data:
                if not is_valid_email(data['email']):
                    return Response("Incorrect email format", status=409)
                user.email = data['email']
            
            if 'username' not in data and 'email' not in data:
                return {"message": "No username or email provided"}, 400
            
            db.session.commit()
            return {"message": "User updated successfully"}, 200

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
        """
        try:
            user = User.query.filter_by(id = userId).first()
            if user is None:
                return {"message": "User not found"}, 404

            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
