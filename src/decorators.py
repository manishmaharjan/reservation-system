"""
This module contains decorators for verifying user authentication and authorization.

Decorators:
- require_admin: Checks if the user making the request is an admin.
- require_user: Requires the user to be authenticated with a valid API key.
"""

from functools import wraps

from flask import request, Response
from werkzeug.exceptions import Unauthorized

from src import db
from src.models import ApiKey


# Function to verify if the request comes from an admin righted user
def require_admin(func):
    """
    Decorator that checks if the user making the request is an admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.

    Raises:
        Unauthorized: If the user is an admin or the API key is invalid.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            key_hash = ApiKey.key_hash(request.headers.get("Api-key").strip())
            db_key = ApiKey.query.filter_by(key=key_hash).first()
        except Exception as exc:
            return Response("The provided Api-key does not belong to an admin account", status = 401)
        if db_key and db_key.admin:
            return func(*args, **kwargs)
        return Response("The provided Api-key does not belong to an admin account", status = 401)
    return wrapper


# Function to verify if the request comes from an actual user
def require_user(func):
    """
    Decorator that requires the user to be authenticated with a valid API key.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function, with the user object as "apiKeyUser".

    Raises:
        Unauthorized: If the user is not authenticated or the API key is invalid.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # The token will go in a special header named: "Api-key"
        try:
            key_hash = ApiKey.key_hash(request.headers.get("Api-key").strip())
            db_key = ApiKey.query.filter_by(key=key_hash).first()
        except Exception as exc:
            return Response("Incorrect api key.", status = 401)
        if db_key:
            kwargs["apiKeyUser"] = db_key.user
            return func(*args, **kwargs)
        return Response("Incorrect api key.", status = 401)


    return wrapper
