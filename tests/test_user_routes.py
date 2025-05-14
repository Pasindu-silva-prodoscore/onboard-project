import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.routes.users import users_bp  
from app.models.user import User, db  
from datetime import datetime
from unittest.mock import patch, Mock

# Fixture to set up Flask app and in-memory database
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    app.config["JWT_SECRET_KEY"] = "test-secret-key" 
    db.init_app(app)
    app.register_blueprint(users_bp, url_prefix='/api')
    
    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(404)
    def error_handler(error):
        return {"error": str(error.description)}, error.code

    return app

# Fixture to set up the test client within app context
@pytest.fixture
def client(app):
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()

# Mock User model methods
@pytest.fixture
def mock_user():
    with patch('app.models.user.User') as mock:
        mock.get_by_username.return_value = None
        mock.create.return_value = Mock(username="testuser", id=1)
        mock.verify_password.return_value = True
        yield mock

# Mock JWT utilities
@pytest.fixture
def mock_jwt():
    with patch('app.utils.jwt_utils') as mock:
        mock.create_jwt_token.return_value = "mocked_token"
        mock.verify_jwt_token.return_value = {"sub": 1}
        yield mock

# Test POST /api/register 
def test_register_success(client, mock_user):
    data = {"username": "newuser", "password": "password123"}
    response = client.post('/api/register', json=data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User registered successfully"
    assert data["username"] == "newuser"
    mock_user.create.assert_called_once_with("newuser", "password123")

# Test POST /api/register (missing JSON)
def test_register_missing_json(client, mock_user):
    response = client.post('/api/register', data="not_json")
    assert response.status_code == 400
    data = response.get_json()
    assert "Request body must be JSON" in data["error"]

# Test POST /api/login (successful login)
def test_login_success(client, mock_user, mock_jwt):
    data = {"username": "testuser", "password": "password123"}
    mock_user.get_by_username.return_value = Mock(password_hash="hashed_password")
    response = client.post('/api/token', json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    mock_jwt.create_jwt_token.assert_any_call(1, token_type='access')
    mock_jwt.create_jwt_token.assert_any_call(1, token_type='refresh')

# Test POST /api/login (invalid credentials)
def test_login_invalid_credentials(client, mock_user):
    data = {"username": "testuser", "password": "wrongpass"}
    mock_user.get_by_username.return_value = Mock(password_hash="hashed_password")
    mock_user.verify_password.return_value = False
    response = client.post('/api/token', json=data)
    assert response.status_code == 401
    data = response.get_json()
    assert "Invalid username or password" in data["error"]

# Test POST /api/refresh (successful refresh)
def test_refresh_success(client, mock_jwt):
    headers = {"Authorization": "Bearer mocked_token"}
    response = client.post('/api/refresh', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    mock_jwt.verify_jwt_token.assert_called_once_with("mocked_token", token_type='refresh')

# Test POST /api/refresh (invalid token)
def test_refresh_invalid_token(client, mock_jwt):
    headers = {"Authorization": "Bearer invalid_token"}
    mock_jwt.verify_jwt_token.return_value = None
    response = client.post('/api/refresh', headers=headers)
    assert response.status_code == 401
    data = response.get_json()
    assert "Invalid or expired refresh token" in data["error"]