import base64
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.user import User, db  # Adjust import based on your structure

# Fixture to set up Flask app and in-memory database
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

# Fixture to set up the database within app context
@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

# Fixture for sample user data
@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "password": "password123"
    }

# Test User.get_by_username
def test_get_by_username(setup_db, user_data):
    user = User(username=user_data["username"], password_hash="test_hash")
    db.session.add(user)
    db.session.commit()
    
    fetched_user = User.get_by_username(user_data["username"])
    assert fetched_user is not None
    assert fetched_user.username == user_data["username"]
    
    # Test with non-existent username
    assert User.get_by_username("nonexistent") is None

# Test User.create
def test_create_user(setup_db, user_data):
    user = User.create(user_data["username"], user_data["password"])
    assert user is not None
    assert user.username == user_data["username"]
    assert user.password_hash.startswith("pbkdf2-sha256$")
    
    # Verify user exists in database
    fetched_user = User.get_by_username(user_data["username"])
    assert fetched_user is not None
    assert fetched_user.password_hash == user.password_hash

# Test User.generate_password_hash
def test_generate_password_hash():
    password = "testpassword"
    hash_value = User.generate_password_hash(password)
    parts = hash_value.split('$')
    assert len(parts) == 4
    assert parts[0] == "pbkdf2-sha256"
    assert base64.b64decode(parts[1])  # Valid base64 salt
    assert int(parts[2]) == 100000  # Default iterations
    assert base64.b64decode(parts[3])  # Valid base64 key
    
    # Test with custom iterations
    hash_value_custom = User.generate_password_hash(password, iterations=50000)
    parts_custom = hash_value_custom.split('$')
    assert int(parts_custom[2]) == 50000

# Test User.verify_password
def test_verify_password(setup_db, user_data):
    # Create a hash and user
    password = user_data["password"]
    hash_value = User.generate_password_hash(password)
    user = User(username=user_data["username"], password_hash=hash_value)
    db.session.add(user)
    db.session.commit()
    
    # Verify correct password
    assert User.verify_password(hash_value, password) is True
    
    # Verify incorrect password
    assert User.verify_password(hash_value, "wrongpassword") is False
    
    # Test with invalid hash format
    assert User.verify_password("invalid$hash$format", password) is False