from flask import Blueprint, request, jsonify, abort
from ..middleware.auth import require_api_token
from ..models.pin import Pin
from datetime import datetime

pins_bp = Blueprint('pins', __name__)

# GET all pins with filtering and ordering
@pins_bp.route('/pins', methods=['GET'])
def get_pins():
    author = request.args.get('author')
    order_by = request.args.get('order_by', 'date_created')
    order_dir = request.args.get('order_dir', 'desc')

    valid_fields = ['title', 'date_created', 'author']
    if order_by not in valid_fields:
        abort(400, description=f"Invalid order_by field. Must be one of {valid_fields}")

    if order_dir not in ['asc', 'desc']:
        abort(400, description="order_dir must be 'asc' or 'desc'")

    pins = Pin.get_all(author_filter=author, order_by=order_by, order_dir=order_dir)
    pins_data = [pin.to_dict() for pin in pins]

    return jsonify({"data": pins_data, "count": len(pins_data)}), 200

# GET a single pin by ID
@pins_bp.route('/pins/<int:pin_id>', methods=['GET'])
def get_pin(pin_id):
    pin = Pin.get_by_id(pin_id)
    if not pin:
        abort(404, description="Pin not found")
    return jsonify({"data": pin.to_dict()}), 200

# POST to create a new pin
@pins_bp.route('/pins', methods=['POST'])
def create_pin():
    if not request.json:
        abort(400, description="Request body must be JSON")
    
    required_fields = ['title', 'body', 'image_link', 'author']
    if not all(field in request.json for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    pin_data = {
        "title": request.json["title"],
        "body": request.json["body"],
        "image_link": request.json["image_link"],
        "author": request.json["author"],
        "date_created": datetime.utcnow()
    }
    pin = Pin.create(pin_data)
    return jsonify({"data": pin.to_dict()}), 201

# PUT to update a pin
@pins_bp.route('/pins/<int:pin_id>', methods=['PUT'])
@require_api_token
def update_pin(pin_id):
    pin = Pin.get_by_id(pin_id)
    if not pin:
        abort(404, description="Pin not found")
    if not request.json:
        abort(400, description="Request body must be JSON")

    pin_data = {
        "title": request.json.get("title", pin.title),
        "body": request.json.get("body", pin.body),
        "image_link": request.json.get("image_link", pin.image_link),
        "author": request.json.get("author", pin.author)
    }
    pin = Pin.update(pin_id, pin_data)
    if not pin:
        abort(404, description="Pin not found")
    return jsonify({"data": pin.to_dict()}), 200

# DELETE a pin
@pins_bp.route('/pins/<int:pin_id>', methods=['DELETE'])
@require_api_token
def delete_pin(pin_id):
    if not Pin.delete(pin_id):
        abort(404, description="Pin not found")
    return jsonify({"message": "Pin deleted"}), 200