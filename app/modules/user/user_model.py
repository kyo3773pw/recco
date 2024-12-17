from werkzeug.security import generate_password_hash, check_password_hash
from ..database.db import Database
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self):
        self.db = Database()

    def create_session(self, user_id):
        query = """
        INSERT INTO user_sessions (user_id, created_at, expires_at) 
        VALUES (?, ?, ?)
        """
        expires_at = datetime.now() + timedelta(hours=24)
        try:
            cursor = self.db.execute_query(
                query, 
                (user_id, datetime.now(), expires_at)
            )
            logger.info(f"Created session for user {user_id}")
            return cursor.lastrowid if cursor else None
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None

    def validate_session(self, session_id):
        query = """
        SELECT user_id FROM user_sessions 
        WHERE id = ? AND expires_at > ? AND revoked = 0
        """
        try:
            cursor = self.db.execute_query(
                query, 
                (session_id, datetime.now())
            )
            result = cursor.fetchone() if cursor else None
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None

    def revoke_session(self, session_id):
        query = "UPDATE user_sessions SET revoked = 1 WHERE id = ?"
        try:
            self.db.execute_query(query, (session_id,))
            logger.info(f"Revoked session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            return False