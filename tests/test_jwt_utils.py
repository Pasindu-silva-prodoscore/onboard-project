import pytest
from datetime import timedelta
from app import create_app
import jwt

# Set up the Flask app for testing
@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    yield app

# Fixture to mock current_app within the app context
@pytest.fixture
def app_context(app):
    with app.app_context():
        yield

# Test create_jwt_token for access token
def test_create_jwt_token_access(app_context):
    from app.utils.jwt_utils import create_jwt_token
    
    user_id = "123"
    token = create_jwt_token(user_id, "access")
    
    payload = jwt.decode(token, "jwt-secret-key", algorithms=["HS256"])
    
    assert payload["sub"] == user_id
    assert payload["type"] == "access"

# Test create_jwt_token for refresh token
def test_create_jwt_token_refresh(app_context):
    from app.utils.jwt_utils import create_jwt_token
    user_id = "123"
    token = create_jwt_token(user_id, "refresh")
    
    payload = jwt.decode(token, "jwt-secret-key", algorithms=["HS256"])
    
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"

# Test create_jwt_token with invalid token type
def test_create_jwt_token_invalid_type(app_context):
    from app.utils.jwt_utils import create_jwt_token
    
    with pytest.raises(ValueError) as exc_info:
        create_jwt_token("123", "invalid")
    assert str(exc_info.value) == "token_type must be 'access' or 'refresh'"

# Test verify_jwt_token for a valid access token
def test_verify_jwt_token_valid_access(app_context):
    from app.utils.jwt_utils import create_jwt_token, verify_jwt_token
    
    user_id = "123"
    token = create_jwt_token(user_id, "access")
    
    payload = verify_jwt_token(token, "access")
    
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["type"] == "access"

# Test verify_jwt_token with wrong token type
def test_verify_jwt_token_wrong_type(app_context):
    from app.utils.jwt_utils import create_jwt_token, verify_jwt_token
    
        
    token = create_jwt_token("123", "access")
    
    payload = verify_jwt_token(token, "refresh")
    
    assert payload is None


# Test verify_jwt_token with invalid token
def test_verify_jwt_token_invalid(app_context):
    from app.utils.jwt_utils import verify_jwt_token
    
    invalid_token = "invalid.token.here"
    
    payload = verify_jwt_token(invalid_token, "access")
    
    assert payload is None