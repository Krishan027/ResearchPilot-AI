
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.research_repository import (
    save_session,
    get_session,
    list_sessions,
    delete_session,
)

router = APIRouter(
    prefix="/api/history",
    tags=["Research History"],
)


class ResearchMessage(BaseModel):
    id: str
    role: str
    text: str
    citations: list[dict] = Field(default_factory=list)
    confidence: int | float | str | dict | None = None
    created_at: str | None = None


class ResearchSession(BaseModel):
    id: str
    title: str = "New research"
    document_id: str = ""
    file_name: str = ""
    created_at: str | None = None
    messages: list[ResearchMessage] = Field(default_factory=list)


@router.get("")
def get_research_history(q: str | None = None):
    """List saved sessions, optionally filtered by title."""
    sessions = list_sessions()

    if q and q.strip():
        query = q.strip().casefold()
        sessions = [
            session
            for session in sessions
            if query in (session.get("title") or "").casefold()
        ]

    return {"sessions": sessions}


@router.post("")
def create_or_update_research_session(session: ResearchSession):
    """Create or update a saved research session."""
    now = datetime.now(timezone.utc).isoformat()

    session_data = session.model_dump()
    session_data["created_at"] = session.created_at or now
    session_data["updated_at"] = now

    save_session(session_data)

    return {
        "message": "Research session saved successfully",
        "session_id": session.id,
    }


@router.get("/{session_id}")
def get_research_session(session_id: str):
    """Retrieve a saved session and its messages."""
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Research session not found",
        )

    return session


@router.delete("/{session_id}")
def remove_research_session(session_id: str):
    """Delete a saved research session."""
    deleted = delete_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Research session not found",
        )

    return {
        "message": "Research session deleted successfully",
        "session_id": session_id,
    }
