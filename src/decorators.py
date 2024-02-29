from functools import wraps
from http.client import FORBIDDEN
from flask import request
from src.models import ApiKey
from src import db
from flask import Response
from werkzeug.exceptions import Unauthorized

# Function to verify if the request comes from an admin righted user
def require_admin(func):
    def wrapper(*args, **kwargs):
        # The token will go in a special header named: "Api-key"
        try:
            key_hash = ApiKey.key_hash(request.headers.get("Api-key").strip())
            db_key = ApiKey.query.filter_by(key=key_hash).first()
        except:
            raise Unauthorized()
        if db_key and db_key.admin:
            return func(db.key.user, *args, **kwargs)
        raise Unauthorized()
    return wrapper

# Function to verify if the request comes from an actual user
def require_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # The token will go in a special header named: "Api-key"
        try:
            key_hash = ApiKey.key_hash(request.headers.get("Api-key").strip())
            db_key = ApiKey.query.filter_by(key= key_hash).first()
        except:
            raise Unauthorized()
        if db_key:
            kwargs['user'] = db_key.user
            return func(*args, **kwargs)
        raise Unauthorized()
    return wrapper