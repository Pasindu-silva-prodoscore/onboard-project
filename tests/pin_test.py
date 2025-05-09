import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch
from flask import Flask
from app.utils.jwt import create_jwt_token, verify_jwt_token
from app import create_app

@pytest.fixture
def app():
    """Create a Flask app with test configuration."""
    app = create_app()
    with app.app_context():
        yield app

@pytest.fixture
def mock_datetime():
    """Mock datetime.now() to return a fixed timestamp."""
    fixed_datetime = datetime(2025, 5, 9, 12, 0, 0)  # Fixed time for consistent tests
    with patch('app.utils.jwt_utils.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_datetime
        yield fixed_datetime

def test_create_jwt_token_access(app, mock_datetime):
    """Test creating an access token."""
    with app.app_context():
        token = create_jwt_token(user_id=1, token_type='access')
        # Decode token to verify payload
        payload = jwt.decode(token, 'jwt-secret-key', algorithms=['HS256'])
        
        assert payload['sub'] == 1
        assert payload['type'] == 'access'
        assert payload['iat'] == int(mock_datetime.timestamp())
        assert payload['exp'] == int((mock_datetime + timedelta(minutes=10)).timestamp())

def test_create_jwt_token_refresh(app, mock_datetime):
    """Test creating a refresh token."""
    with app.app_context():
        token = create_jwt_token(user_id=2, token_type='refresh')
        payload = jwt.decode(token, 'jwt-secret-key', algorithms=['HS256'])
        
        assert payload['sub'] == 2
        assert payload['type'] == 'refresh'
        assert payload['iat'] == int(mock_datetime.timestamp())
        assert payload['exp'] == int((mock_datetime + timedelta(days=7)).timestamp())

def test_create_jwt_token_invalid_token_type(app):
    """Test creating a token with invalid token_type."""
    with app.app_context():
        with pytest.raises(ValueError) as exc_info:
            create_jwt_token(user_id=1, token_type='invalid')
        assert str(exc_info.value) == "token_type must be 'access' or 'refresh'"

def test_verify_jwt_token_valid_access(app, mock_datetime):
    """Test verifying a valid access token."""
    with app.app_context():
        token = create_jwt_token(user_id=1, token_type='access')
        payload = verify_jwt_token(token, token_type='access')
        
        assert payload is not None
        assert payload['sub'] == 1
        assert payload['type'] == 'access'
        assert payload['iat'] == int(mock_datetime.timestamp())
        assert payload['exp'] == int((mock_datetime + timedelta(minutes=10)).timestamp())

def test_verify_jwt_token_valid_refresh(app, mock_datetime):
    """Test verifying a valid refresh token."""
    with app.app_context():
        token = create_jwt_token(user_id=2, token_type='refresh')
        payload = verify_jwt_token(token, token_type='refresh')
        
        assert payload is not None
        assert payload['sub'] == 2
        assert payload['type'] == 'refresh'
        assert payload['iat'] == int(mock_datetime.timestamp())
        assert payload['exp'] == int((mock_datetime + timedelta(days=7)).timestamp())

def test_verify_jwt_token_wrong_type(app, mock_datetime):
    """Test verifying a token with the wrong token_type."""
    with app.app_context():
        token = create_jwt_token(user_id=1, token_type='access')
        payload = verify_jwt_token(token, token_type='refresh')
        assert payload is None

def test_verify_jwt_token_expired(app, mock_datetime):
    """Test verifying an expired token."""
    with app.app_context():
        # Create an expired token
        expired_datetime = datetime(2025, 5, 9, 12, 0, 0)
        with patch('app.utils.jwt_utils.datetime') as mock_dt:
            mock_dt.now.return_value = expired_datetime - timedelta(minutes=11)
            token = create_jwt_token(user_id=1, token_type='access')
        
        # Verify with current time
        payload = verify_jwt_token(token, token_type='access')
        assert payload is None

def test_verify_jwt_token_invalid_signature(app, mock_datetime):
    """Test verifying a token with an invalid signature."""
    with app.app_context():
        # Create a token with a different secret
        payload = {
            'sub': 1,
            'iat': int(mock_datetime.timestamp()),
            'exp': int((mock_datetime + timedelta(minutes=10)).timestamp()),
            'type': 'access'
        }
        token = jwt.encode(payload, 'wrong-secret-key', algorithm='HS256')
        
        result = verify_jwt_token(token, token_type='access')
        assert result is None

def test_verify_jwt_token_missing_fields(app, mock_datetime):
    """Test verifying a token with missing required fields."""
    with app.app_context():
        # Create a token with missing 'sub'
        payload = {
            'iat': int(mock_datetime.timestamp()),
            'exp': int((mock_datetime + timedelta(minutes=10)).timestamp()),
            'type': 'access'
        }
        token = jwt.encode(payload, 'jwt-secret-key', algorithm='HS256')
        
        result = verify_jwt_token(token, token_type='access')
        assert result is None

def test_verify_jwt_token_malformed(app):
    """Test verifying a malformed token."""
    with app.app_context():
        result = verify_jwt_token("invalid.token.string", token_type='access')
        assert result is None