import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.routes.pins import pins_bp  
from app.models.pin import Pin, db  
from datetime import datetime
from unittest.mock import patch

# Fixture to set up Flask app and in-memory database
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False  
    app.config["JWT_SECRET_KEY"] = "test-secret-key"  
    db.init_app(app)
    app.register_blueprint(pins_bp, url_prefix='/api')
    
    # Custom error handler to return JSON instead of HTML
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

# Fixture for sample pin data
@pytest.fixture
def pin_data():
    return {
        "title": "Test Pin",
        "body": "This is a test pin.",
        "image_link": "http://example.com/image.jpg",
        "author": "Alice",
        "date_created": datetime.fromisoformat("2025-05-14T11:25:00")  
    }

# Mock authenticate middleware 
@pytest.fixture
def mock_authenticate():
    with patch('app.utils.jwt_utils.verify_jwt_token') as mock_verify:
        mock_verify.return_value = {"user_id": 1}  
        yield mock_verify

# Test GET /pins 
def test_get_pins(client, pin_data):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    response = client.get('/api/pins')
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 1
    assert data["data"][0]["title"] == "Test Pin"

# Test GET /pins with author filter
def test_get_pins_with_author_filter(client, pin_data):
    pin1 = Pin(**pin_data)
    pin2 = Pin(**{**pin_data, "author": "Bob"})
    db.session.add_all([pin1, pin2])
    db.session.commit()
    
    response = client.get('/api/pins?author=Alice')
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 1
    assert data["data"][0]["author"] == "Alice"

# Test GET /pins/<pin_id>
def test_get_pin(client, pin_data):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    response = client.get(f'/api/pins/{pin.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["title"] == "Test Pin"

# Test GET /pins/<pin_id> with invalid ID
def test_get_pin_not_found(client):
    response = client.get('/api/pins/999')
    assert response.status_code == 404
    data = response.get_json()
    assert "Pin not found" in data["error"]

# Test POST /pins
def test_create_pin(client, pin_data, mock_authenticate):
    headers = {"Authorization": "Bearer valid_token"}
    response = client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["title"] == "Test Pin"
    assert data["data"]["author"] == "Alice"
    assert "date_created" in data["data"]

# Test POST /pins with missing fields
def test_create_pin_missing_fields(client, mock_authenticate):
    headers = {"Authorization": "Bearer valid_token"}
    invalid_data = {"title": "Test", "body": "Body"}  
    response = client.post('/api/pins', json=invalid_data, headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required fields" in data["error"]

# Test POST /pins with invalid JSON
def test_create_pin_invalid_json(client, mock_authenticate):
    headers = {"Authorization": "Bearer valid_token"}
    response = client.post('/api/pins', data="invalid", headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "Request body must be JSON" in data["error"]

# Test PUT /pins/<pin_id>
def test_update_pin(client, pin_data, mock_authenticate):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    headers = {"Authorization": "Bearer valid_token"}
    updated_data = {"title": "Updated Pin", "author": "Bob"}
    response = client.put(f'/api/pins/{pin.id}', json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["title"] == "Updated Pin"
    assert data["data"]["author"] == "Bob"

# Test PUT /pins/<pin_id> with invalid JSON
def test_update_pin_invalid_json(client, pin_data, mock_authenticate):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    headers = {"Authorization": "Bearer valid_token"}
    response = client.put(f'/api/pins/{pin.id}', data="invalid", headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "Request body must be JSON" in data["error"]

# Test DELETE /pins/<pin_id>
def test_delete_pin(client, pin_data, mock_authenticate):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    headers = {"Authorization": "Bearer valid_token"}
    response = client.delete(f'/api/pins/{pin.id}', headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Pin deleted"
    assert db.session.get(Pin, pin.id) is None

# Test DELETE /pins/<pin_id> with invalid ID
def test_delete_pin_not_found(client, mock_authenticate):
    headers = {"Authorization": "Bearer valid_token"}
    response = client.delete('/api/pins/999', headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert "Pin not found" in data["error"]