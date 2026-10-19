
import json
from datetime import datetime, timezone

from app.core.database import get_connection


def _now():
    return datetime.now(timezone.utc).isoformat()


def save_session(session):
    """Create or update a research session and its messages."""
    now = _now()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO research_sessions (
                id, title, document_id, file_name, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                document_id = excluded.document_id,
                file_name = excluded.file_name,
                updated_at = excluded.updated_at
            """,
            (
                session["id"],
                session.get("title", "New research"),
                session.get("document_id", ""),
                session.get("file_name", ""),
                session.get("created_at", now),
                now,
            ),
        )

        connection.execute(
            "DELETE FROM research_messages WHERE session_id = ?",
            (session["id"],),
        )

        for message in session.get("messages", []):
            connection.execute(
                """
                INSERT INTO research_messages (
                    id, session_id, role, text, citations_json,
                    confidence_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message["id"],
                    session["id"],
                    message["role"],
                    message.get("text", ""),
                    json.dumps(message.get("citations", [])),
                    json.dumps(message.get("confidence"))
                    if message.get("confidence") is not None
                    else None,
                    message.get("created_at", now),
                ),
            )


def get_session(session_id):
    """Return one session and its messages, or None if not found."""
    with get_connection() as connection:
        session_row = connection.execute(
            "SELECT * FROM research_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()

        if session_row is None:
            return None

        session = dict(session_row)
        message_rows = connection.execute(
            """
            SELECT * FROM research_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        ).fetchall()

        session["messages"] = []
        for row in message_rows:
            message = dict(row)
            message["citations"] = json.loads(message.pop("citations_json"))
            confidence_json = message.pop("confidence_json")
            message["confidence"] = (
                json.loads(confidence_json)
                if confidence_json is not None
                else None
            )
            session["messages"].append(message)

        return session


def list_sessions():
    """Return session summaries, newest activity first."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                s.id, s.title, s.document_id, s.file_name,
                s.created_at, s.updated_at,
                COUNT(m.id) AS message_count
            FROM research_sessions AS s
            LEFT JOIN research_messages AS m ON m.session_id = s.id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def delete_session(session_id):
    """Delete a session and its messages."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM research_sessions WHERE id = ?",
            (session_id,),
        )
        return cursor.rowcount > 0
