import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_jwt_token(user_id, token_type):
    """Generate a JWT token (access or refresh) for the given user ID."""
    if token_type not in ['access', 'refresh']:
        raise ValueError("token_type must be 'access' or 'refresh'")

    expires_delta = (
        current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        if token_type == 'access'
        else current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
    )
    issued_at = datetime.utcnow()
    expires_at = issued_at + expires_delta

    payload = {
        'sub': user_id,
        'iat': int(issued_at.timestamp()),
        'exp': int(expires_at.timestamp()),
        'type': token_type
    }

    secret = current_app.config['JWT_SECRET_KEY']
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def verify_jwt_token(token, token_type):
    """Verify a JWT token and return its payload if valid."""
    try:
        secret = current_app.config['JWT_SECRET_KEY']
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        
        if payload.get('type') != token_type:
            return None
        
        if 'sub' not in payload or 'iat' not in payload or 'exp' not in payload:
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None