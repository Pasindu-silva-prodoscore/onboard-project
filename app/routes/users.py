from flask import Blueprint, request, jsonify, abort
from ..models.user import User
from ..utils.jwt_utils import create_jwt_token, verify_jwt_token

users_bp = Blueprint('users', __name__)

# Register a new user
@users_bp.route('/register', methods=['POST'])
def register():
    if not request.json:
        abort(400, description="Request body must be JSON")
    
    required_fields = ['username', 'password']
    if not all(field in request.json for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    username = request.json['username']
    password = request.json['password']

    if User.get_by_username(username):
        abort(400, description="Username already exists")

    user = User.create(username, password)
    return jsonify({"message": "User registered successfully", "username": user.username}), 201

# Obtain access and refresh tokens
@users_bp.route('/token', methods=['POST'])
def login():
    if not request.json:
        abort(400, description="Request body must be JSON")
    
    required_fields = ['username', 'password']
    if not all(field in request.json for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    username = request.json['username']
    password = request.json['password']

    user = User.get_by_username(username)
    if not user or not User.verify_password(user.password_hash, password):
        abort(401, description="Invalid username or password")

    access_token = create_jwt_token(user.id, token_type='access')
    refresh_token = create_jwt_token(user.id, token_type='refresh')

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# Refresh access token using refresh token
@users_bp.route('/refresh', methods=['POST'])
def refresh():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401, description="Missing or invalid Authorization header")
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token, token_type='refresh')
    if not payload:
        abort(401, description="Invalid or expired refresh token")

    user_id = payload['sub']
    access_token = create_jwt_token(user_id, token_type='access')
    return jsonify({"access_token": access_token}), 200