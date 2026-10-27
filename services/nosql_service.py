import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger('mysterymart.nosql')

# In-memory storage fallback if MongoDB is not configured or unavailable
_IN_MEMORY_CHAT_LOGS: List[Dict[str, Any]] = []
_IN_MEMORY_FEEDBACK: List[Dict[str, Any]] = []


class NoSQLService:
    """Service to manage MongoDB storage for chat logs and customer feedback."""
    def __init__(self, mongo_uri: Optional[str] = None, db_name: str = 'mysterymart_nosql'):
        self.mongo_uri = mongo_uri or os.environ.get('MONGODB_URI')
        self.db_name = db_name or os.environ.get('MONGODB_DB_NAME', 'mysterymart_nosql')
        self.client = None
        self.db = None
        self._connected = False
        self._init_connection()

    def _init_connection(self):
        """Attempt to connect to MongoDB if URI is configured."""
        if not self.mongo_uri:
            logger.info("No MONGODB_URI configured. NoSQL service operating in safe in-memory fallback mode.")
            return

        try:
            from pymongo import MongoClient
            # Set a 3-second server selection timeout to avoid blocking startup
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=3000)
            # Test ping
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self._connected = True
            logger.info("Successfully connected to MongoDB (%s)", self.db_name)
        except Exception as e:
            logger.warning("Could not connect to MongoDB (%s). Using safe in-memory fallback. Reason: %s", self.mongo_uri, e)
            self._connected = False
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        """Check if connected to live MongoDB."""
        if not self._connected or not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def save_chat_log(self, session_id: str, role: str, message: str, meta: Optional[Dict[str, Any]] = None) -> bool:
        """Store chat interaction in MongoDB or in-memory fallback."""
        record = {
            'session_id': session_id,
            'role': role,  # 'user' or 'assistant'
            'message': message,
            'meta': meta or {},
            'timestamp': datetime.utcnow()
        }

        if self.is_connected() and self.db is not None:
            try:
                self.db['chat_logs'].insert_one(record)
                return True
            except Exception as e:
                logger.error("Failed to insert chat log into MongoDB: %s", e)

        # In-memory fallback
        _IN_MEMORY_CHAT_LOGS.append(record)
        return True

    def get_recent_chat(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversation turns for a session."""
        if self.is_connected() and self.db is not None:
            try:
                cursor = self.db['chat_logs'].find({'session_id': session_id}).sort('timestamp', 1).limit(limit)
                results = []
                for doc in cursor:
                    doc['id'] = str(doc.get('_id', ''))
                    doc.pop('_id', None)
                    results.append(doc)
                return results
            except Exception as e:
                logger.error("Error reading chat logs from MongoDB: %s", e)

        # Fallback to in-memory
        matches = [log for log in _IN_MEMORY_CHAT_LOGS if log['session_id'] == session_id]
        return matches[-limit:]

    def save_feedback(self, session_id: str, rating: int, comment: str = '', email: str = '') -> bool:
        """Store customer rating and feedback."""
        record = {
            'session_id': session_id,
            'rating': max(1, min(5, int(rating))),
            'comment': comment.strip(),
            'email': email.strip(),
            'timestamp': datetime.utcnow()
        }

        if self.is_connected() and self.db is not None:
            try:
                self.db['customer_feedback'].insert_one(record)
                return True
            except Exception as e:
                logger.error("Failed to insert customer feedback into MongoDB: %s", e)

        _IN_MEMORY_FEEDBACK.append(record)
        return True

    def get_feedback_count(self) -> int:
        """Return total feedback records count."""
        if self.is_connected() and self.db is not None:
            try:
                return self.db['customer_feedback'].count_documents({})
            except Exception:
                pass
        return len(_IN_MEMORY_FEEDBACK)


# Singleton instance
nosql_service = NoSQLService()
