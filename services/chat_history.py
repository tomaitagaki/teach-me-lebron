"""
Chat history management with SQLite database.

Provides conversation persistence and retrieval with context window management.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
import json
from logging_config import get_logger

logger = get_logger(__name__)


class ChatHistoryService:
    """Service for managing chat conversation history."""

    def __init__(self, db_path: str = "data/chat_history.db"):
        """Initialize the chat history service with SQLite database."""
        self.db_path = db_path

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_database()
        logger.info(f"ChatHistoryService initialized with database at {db_path}")

    def _init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    clips TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_created (user_id, created_at)
                )
            """)

            # Create sessions table for tracking conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.debug("Database schema initialized")

    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        clips: Optional[List[Dict]] = None
    ) -> int:
        """
        Add a message to chat history.

        Args:
            user_id: User identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            clips: Optional list of video clips associated with this message

        Returns:
            Message ID
        """
        clips_json = json.dumps(clips) if clips else None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (user_id, role, content, clips)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, role, content, clips_json)
            )
            message_id = cursor.lastrowid
            conn.commit()

            logger.debug(f"Added {role} message for user {user_id}: {content[:50]}...")
            return message_id

    def get_conversation_history(
        self,
        user_id: str,
        limit: int = 20,
        include_clips: bool = False
    ) -> List[Dict]:
        """
        Get recent conversation history for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of messages to retrieve
            include_clips: Whether to include clip data

        Returns:
            List of message dictionaries with role, content, and optional clips
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT role, content, clips, created_at
                FROM messages
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit)
            )

            messages = []
            for row in cursor.fetchall():
                message = {
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"]
                }

                if include_clips and row["clips"]:
                    message["clips"] = json.loads(row["clips"])

                messages.append(message)

            # Reverse to get chronological order
            messages.reverse()

            logger.debug(f"Retrieved {len(messages)} messages for user {user_id}")
            return messages

    def get_context_for_llm(
        self,
        user_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get conversation context formatted for LLM API.

        Returns messages in the format needed for OpenRouter API,
        limiting to recent messages to stay within context window.

        Args:
            user_id: User identifier
            max_messages: Maximum number of recent messages to include

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        messages = self.get_conversation_history(user_id, limit=max_messages)

        # Format for LLM API (only role and content)
        llm_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]

        logger.debug(f"Prepared {len(llm_messages)} messages as LLM context for user {user_id}")
        return llm_messages

    def clear_history(self, user_id: str) -> int:
        """
        Clear all chat history for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of messages deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM messages WHERE user_id = ?",
                (user_id,)
            )
            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Cleared {deleted_count} messages for user {user_id}")
            return deleted_count

    def get_message_count(self, user_id: str) -> int:
        """Get total message count for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM messages WHERE user_id = ?",
                (user_id,)
            )
            count = cursor.fetchone()[0]
            return count
