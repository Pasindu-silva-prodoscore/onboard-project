import os
from functools import wraps
from flask import request, jsonify
from ..utils.jwt import create_jwt_token, verify_jwt_token

def authenticate(f):
    """Decorator to authenticate a user using JWT."""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Missing token"}), 401
        token = token.split(" ")[1] 
        payload = verify_jwt_token(token, token_type='access')
        print (f"Payload: {payload}")
        if not payload:
            return jsonify({"message": "Invalid token"}), 401
        return await f(*args, **kwargs)

    return decorated_function