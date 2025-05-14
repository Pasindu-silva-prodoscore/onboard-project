import pytest
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.pin import Pin, db  

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def pin_data():
    return {
        "title": "Test Pin",
        "body": "This is a test pin.",
        "image_link": "http://example.com/image.jpg",
        "author": "Alice",
        "date_created": datetime(2025, 1, 1, 12, 0, 0)
    }

# Test Pin.to_dict 
def test_pin_to_dict(setup_db, pin_data):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    result = pin.to_dict()
    assert result == {
        "id": pin.id,
        "title": "Test Pin",
        "body": "This is a test pin.",
        "image_link": "http://example.com/image.jpg",
        "author": "Alice",
        "date_created": "2025-01-01T12:00:00"
    }

# Test Pin.get_all 
@pytest.mark.asyncio
async def test_get_all_no_filter(setup_db, pin_data):
    pin1 = Pin(**pin_data)
    pin2 = Pin(**{**pin_data, "title": "Another Pin", "author": "Bob"})
    db.session.add_all([pin1, pin2])
    db.session.commit()
    
    pins = await Pin.get_all()
    assert len(pins) == 2
    assert pins[0].title == "Test Pin"  
    assert pins[1].title == "Another Pin"

# Test Pin.get_all with author filter
@pytest.mark.asyncio
async def test_get_all_author_filter(setup_db, pin_data):
    pin1 = Pin(**pin_data)
    pin2 = Pin(**{**pin_data, "author": "Bob"})
    db.session.add_all([pin1, pin2])
    db.session.commit()
    
    pins = await Pin.get_all(author_filter="alice")
    assert len(pins) == 1
    assert pins[0].author == "Alice"

# Test Pin.get_all with ascending order
@pytest.mark.asyncio
async def test_get_all_order_asc(setup_db, pin_data):
    pin1 = Pin(**pin_data)
    pin2 = Pin(**{**pin_data, "title": "Another Pin"})
    db.session.add_all([pin1, pin2])
    db.session.commit()
    
    pins = await Pin.get_all(order_dir="asc")
    assert len(pins) == 2
    assert pins[0].title == "Test Pin" 
    assert pins[1].title == "Another Pin"

# Test Pin.get_by_id
@pytest.mark.asyncio
async def test_get_by_id(setup_db, pin_data):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    fetched_pin = await Pin.get_by_id(pin.id)
    assert fetched_pin is not None
    assert fetched_pin.title == "Test Pin"

# Test Pin.get_by_id with invalid ID
@pytest.mark.asyncio
async def test_get_by_id_invalid(setup_db):
    fetched_pin = await Pin.get_by_id(999)
    assert fetched_pin is None

# Test Pin.create
@pytest.mark.asyncio
async def test_create_pin(setup_db, pin_data):
    pin = await Pin.create(pin_data)
    assert pin is not None
    assert pin.title == "Test Pin"
    assert pin.author == "Alice"
    
    # Verify in database
    fetched_pin = db.session.get(Pin, pin.id)
    assert fetched_pin is not None
    assert fetched_pin.image_link == "http://example.com/image.jpg"

# Test Pin.update
@pytest.mark.asyncio
async def test_update_pin(setup_db, pin_data):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    updated_data = {
        "title": "Updated Pin",
        "body": "Updated body",
        "image_link": "http://example.com/updated.jpg",
        "author": "Bob",
        "date_created": pin_data["date_created"]  
    }
    updated_pin = await Pin.update(pin.id, updated_data)
    assert updated_pin is not None
    assert updated_pin.title == "Updated Pin"
    assert updated_pin.author == "Bob"
    
    # Verify in database
    fetched_pin = db.session.get(Pin, pin.id)
    assert fetched_pin.title == "Updated Pin"

# Test Pin.update with invalid ID
@pytest.mark.asyncio
async def test_update_pin_invalid(setup_db, pin_data):
    updated_pin = await Pin.update(999, pin_data)
    assert updated_pin is None

# Test Pin.delete
@pytest.mark.asyncio
async def test_delete_pin(setup_db, pin_data):
    pin = Pin(**pin_data)
    db.session.add(pin)
    db.session.commit()
    
    result = await Pin.delete(pin.id)
    assert result is True
    
    # Verify deletion
    fetched_pin = db.session.get(Pin, pin.id)
    assert fetched_pin is None

# Test Pin.delete with invalid ID
@pytest.mark.asyncio
async def test_delete_pin_invalid(setup_db):
    result = await Pin.delete(999)
    assert result is False