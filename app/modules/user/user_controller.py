from flask import jsonify
from .user_model import User
import logging

logger = logging.getLogger(__name__)

class UserController:
    def __init__(self):
        self.user_model = User()

    def register(self, username, password, email):
        if not all([username, password, email]):
            return jsonify({"error": "Missing required fields"}), 400
            
        if self.user_model.create_user(username, password, email):
            return jsonify({"message": "User created successfully"}), 201
        return jsonify({"error": "Error creating user"}), 400

    def login(self, username, password):
        user_id = self.user_model.verify_user(username, password)
        if user_id:
            session_id = self.user_model.create_session(user_id)
            if session_id:
                return jsonify({
                    "message": "Login successful",
                    "user_id": user_id,
                    "session_id": session_id
                }), 200
        return jsonify({"error": "Invalid credentials"}), 401

    def get_user_profile(self, user_id):
        profile = self.user_model.get_user_profile(user_id)
        if profile:
            consultations = self.user_model.get_user_consultations(user_id)
            saved_projects = self.user_model.get_saved_projects(user_id)
            
            return jsonify({
                "profile": profile,
                "consultations": consultations,
                "saved_projects": saved_projects
            }), 200
        return jsonify({"error": "User not found"}), 404