from functools import wraps
from flask import request, jsonify, session
from modules.user.user_model import User
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({"error": "Unauthorized access"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({"error": "Unauthorized access"}), 401
        
        user = User().get_user_by_id(session['user_id'])
        if not user or user[3] != 'admin':  # Asumiendo que el rol está en el índice 3
            logger.warning(f"Non-admin user attempted to access {request.path}")
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated_function