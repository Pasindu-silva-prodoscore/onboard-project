import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_jwt_token(user_id, token_type):
    """Generate a JWT token (access or refresh) for the given user ID."""
    if token_type not in ['access', 'refresh']:
        raise ValueError("token_type must be 'access' or 'refresh'")
    
    if token_type == 'access':
        expires_delta = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    else:
        expires_delta = current_app.config['JWT_REFRESH_TOKEN_EXPIRES']

    issued_at = datetime.now()
    print(f"Token will issued_at: {issued_at}")
    expires_at = issued_at + expires_delta
    print(f"Token will expire at: {expires_at}")

    payload = {
        'sub': user_id,
        'iat': int(issued_at.timestamp()),
        'exp': int(expires_at.timestamp()),
        'type': token_type
    }

    secret = current_app.config['JWT_SECRET_KEY']
    print (secret," secret-1")
    token = jwt.encode(payload, "jwt-secret-key", algorithm='HS256')
    return token

def verify_jwt_token(token, token_type):
    """Verify a JWT token and return its payload if valid."""
    print(f"Verifying token: {token}")
    try:
        secret = current_app.config['JWT_SECRET_KEY']
        print (secret," secret")
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        print(f"Decoded payload: {payload}")
        
        if payload.get('type') != token_type:
            print(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        if 'sub' not in payload or 'iat' not in payload or 'exp' not in payload:
            print("Invalid token payload: missing required fields")
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None