from flask import Blueprint, request, jsonify, session
from .user_controller import UserController
from middleware.auth_middleware import login_required
import logging

logger = logging.getLogger(__name__)
user_bp = Blueprint('user', __name__)
user_controller = UserController()

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not all([username, password, email]):
            return jsonify({"error": "Missing required fields"}), 400
        
        return user_controller.register(username, password, email)
    except Exception as e:
        logger.error(f"Error in registration: {e}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({"error": "Missing credentials"}), 400
        
        result, status_code = user_controller.login(username, password)
        
        if status_code == 200:
            session.permanent = True
            session['user_id'] = result.json['user_id']
            logger.info(f"User {username} logged in successfully")
            
        return result, status_code
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        user_id = session.get('user_id')
        session.clear()
        logger.info(f"User {user_id} logged out")
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def get_profile(user_id):
    try:
        if session.get('user_id') != user_id:
            logger.warning(f"Unauthorized profile access attempt for user {user_id}")
            return jsonify({"error": "Unauthorized access"}), 403
        return user_controller.get_profile(user_id)
    except Exception as e:
        logger.error(f"Error accessing profile: {e}")
        return jsonify({"error": "Internal server error"}), 500