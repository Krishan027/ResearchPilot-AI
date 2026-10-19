
import sqlite3
from pathlib import Path


# Store the database in the backend folder.
DATABASE_PATH = Path(__file__).resolve().parents[2] / "researchpilot.db"


def get_connection():
    """Create a SQLite connection with foreign keys enabled."""
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create the research session and message tables."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'New research',
                document_id TEXT NOT NULL DEFAULT '',
                file_name TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK (role IN ('user', 'assistant')),
                text TEXT NOT NULL,
                citations_json TEXT NOT NULL DEFAULT '[]',
                confidence_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id)
                    REFERENCES research_sessions(id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_research_messages_session
            ON research_messages(session_id)
            """
        )


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DATABASE_PATH}")
