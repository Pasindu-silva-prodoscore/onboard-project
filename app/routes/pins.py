from flask import Blueprint, request, jsonify, abort
from ..models.pin import Pin
from datetime import datetime
from ..middleware.auth import authenticate

pins_bp = Blueprint('pins', __name__)

# GET all pins with filtering and ordering
@pins_bp.route('/pins', methods=['GET'])
async def get_pins():
    author = request.args.get('author')
    order_dir = request.args.get('order_dir', 'desc')

    if order_dir not in ['asc', 'desc']:
        abort(400, description="order_dir must be 'asc' or 'desc'")

    pins = await Pin.get_all(author_filter=author, order_dir=order_dir)
    pins_data = [pin.to_dict() for pin in pins]

    return jsonify({"data": pins_data, "count": len(pins_data)}), 200

# GET a single pin by ID
@pins_bp.route('/pins/<int:pin_id>', methods=['GET'])
async def get_pin(pin_id):
    pin = await Pin.get_by_id(pin_id)
    if not pin:
        abort(404, description="Pin not found")
    return jsonify({"data": pin.to_dict()}), 200

# POST to create a new pin
@pins_bp.route('/pins', methods=['POST'])
@authenticate
async def create_pin():
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
    pin = await Pin.create(pin_data)
    return jsonify({"data": pin.to_dict()}), 201

# PUT to update a pin
@pins_bp.route('/pins/<int:pin_id>', methods=['PUT'])
@authenticate
async def update_pin(pin_id):
    pin = await Pin.get_by_id(pin_id)
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
    pin =await Pin.update(pin_id, pin_data)
    if not pin:
        abort(404, description="Pin not found")
    return jsonify({"data": pin.to_dict()}), 200

# DELETE a pin
@pins_bp.route('/pins/<int:pin_id>', methods=['DELETE'])
@authenticate
async def delete_pin(pin_id):
    if not await Pin.delete(pin_id):
        abort(404, description="Pin not found")
    return jsonify({"message": "Pin deleted"}), 200