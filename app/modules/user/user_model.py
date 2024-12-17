from werkzeug.security import generate_password_hash, check_password_hash
from ..database.db import Database
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self):
        self.db = Database()

    def create_user(self, username, password, email):
        query = """
        INSERT INTO users (username, email, password_hash, created_at) 
        VALUES (%s, %s, %s, %s)
        """
        try:
            password_hash = generate_password_hash(password)
            cursor = self.db.execute_query(
                query, 
                (username, email, password_hash, datetime.now())
            )
            return cursor is not None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def verify_user(self, username, password):
        query = "SELECT id, password_hash FROM users WHERE username = %s"
        try:
            result = self.db.fetch_one(query, (username,))
            if result and check_password_hash(result['password_hash'], password):
                return result['id']
            return None
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None

    def create_session(self, user_id):
        query = """
        INSERT INTO user_sessions (user_id, created_at, expires_at) 
        VALUES (%s, %s, %s)
        """
        expires_at = datetime.now() + timedelta(hours=24)
        try:
            cursor = self.db.execute_query(
                query, 
                (user_id, datetime.now(), expires_at)
            )
            return cursor.lastrowid if cursor else None
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None

    def validate_session(self, session_id):
        query = """
        SELECT user_id FROM user_sessions 
        WHERE id = %s AND expires_at > %s AND revoked = 0
        """
        try:
            result = self.db.fetch_one(
                query, 
                (session_id, datetime.now())
            )
            return result['user_id'] if result else None
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None

    def get_user_profile(self, user_id):
        query = """
        SELECT id, username, email, created_at 
        FROM users WHERE id = %s
        """
        try:
            return self.db.fetch_one(query, (user_id,))
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    def get_user_consultations(self, user_id):
        query = """
        SELECT * FROM consultations 
        WHERE user_id = %s 
        ORDER BY created_at DESC
        """
        try:
            return self.db.fetch_all(query, (user_id,))
        except Exception as e:
            logger.error(f"Error getting user consultations: {e}")
            return []

    def get_saved_projects(self, user_id):
        query = """
        SELECT sp.*, p.* 
        FROM saved_projects sp 
        JOIN projects p ON sp.project_name = p.name 
        WHERE sp.user_id = %s 
        ORDER BY sp.created_at DESC
        """
        try:
            return self.db.fetch_all(query, (user_id,))
        except Exception as e:
            logger.error(f"Error getting saved projects: {e}")
            return []