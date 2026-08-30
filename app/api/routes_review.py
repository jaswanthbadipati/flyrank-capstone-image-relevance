"""API routes for human-in-the-loop review workflow and candidate explanation inspection."""
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models.schemas import (
    ExplainMatchRequest,
    ExplainMatchResponse,
    ReviewActionRequest,
    ReviewActionResponse,
    SuggestionItem
)
from app.services.matcher import explain_candidate_pairing

router = APIRouter(tags=["Review & Inspection"])

@router.post("/match/explain", response_model=ExplainMatchResponse)
def explain_match_route(payload: ExplainMatchRequest):
    """
    Inspect why an image was selected or refused for a given blog post.
    Returns complete Mismatch Guard breakdown and human-readable explanation.
    """
    try:
        return explain_candidate_pairing(post_id=payload.post_id, image_id=payload.image_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/suggestions/{suggestion_id}/approve", response_model=ReviewActionResponse)
def approve_suggestion(suggestion_id: str, payload: Optional[ReviewActionRequest] = None):
    """Approve a suggested image recommendation for a post."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM suggestions WHERE id = ?", (suggestion_id,))
        sugg = cursor.fetchone()
        if not sugg:
            raise HTTPException(status_code=404, detail=f"Suggestion '{suggestion_id}' not found")
            
        cursor.execute("UPDATE suggestions SET status = 'approved' WHERE id = ?", (suggestion_id,))
        
        review_id = str(uuid.uuid4())
        notes = payload.reviewer_notes if payload else "Approved by editor"
        cursor.execute(
            """
            INSERT INTO reviews (id, suggestion_id, action, reviewer_notes, created_at)
            VALUES (?, ?, 'approve', ?, CURRENT_TIMESTAMP)
            """,
            (review_id, suggestion_id, notes)
        )
        
    return ReviewActionResponse(
        suggestion_id=suggestion_id,
        status="approved",
        action_recorded="approve",
        notes=notes,
        reviewed_at=datetime.utcnow().isoformat()
    )

@router.post("/suggestions/{suggestion_id}/reject", response_model=ReviewActionResponse)
def reject_suggestion(suggestion_id: str, payload: Optional[ReviewActionRequest] = None):
    """Reject a suggested image recommendation for a post with optional reviewer feedback."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM suggestions WHERE id = ?", (suggestion_id,))
        sugg = cursor.fetchone()
        if not sugg:
            raise HTTPException(status_code=404, detail=f"Suggestion '{suggestion_id}' not found")
            
        cursor.execute("UPDATE suggestions SET status = 'rejected' WHERE id = ?", (suggestion_id,))
        
        review_id = str(uuid.uuid4())
        notes = payload.reviewer_notes if payload else "Rejected by editor"
        cursor.execute(
            """
            INSERT INTO reviews (id, suggestion_id, action, reviewer_notes, created_at)
            VALUES (?, ?, 'reject', ?, CURRENT_TIMESTAMP)
            """,
            (review_id, suggestion_id, notes)
        )
        
    return ReviewActionResponse(
        suggestion_id=suggestion_id,
        status="rejected",
        action_recorded="reject",
        notes=notes,
        reviewed_at=datetime.utcnow().isoformat()
    )
