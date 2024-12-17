from flask import jsonify
from .user_model import User

class UserController:
    def __init__(self):
        self.user_model = User()

    def register(self, username, password, email):
        if self.user_model.create_user(username, password, email):
            return jsonify({"message": "User created successfully"}), 201
        return jsonify({"error": "Error creating user"}), 400

    def login(self, username, password):
        user_id = self.user_model.verify_user(username, password)
        if user_id:
            # Aquí podrías implementar la generación de token JWT
            return jsonify({
                "message": "Login successful",
                "user_id": user_id
            }), 200
        return jsonify({"error": "Invalid credentials"}), 401

    def get_user_profile(self, user_id):
        user = self.user_model.get_user_by_id(user_id)
        if user:
            return jsonify({
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }), 200
        return jsonify({"error": "User not found"}), 404