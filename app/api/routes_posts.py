"""API routes for blog posts and semantic image suggestions."""
import uuid
import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models.schemas import PostSchema, PostCreate, PostSuggestionsResponse
from app.services.matcher import match_post_to_images
from app.services.embedding import generate_embedding

router = APIRouter(prefix="/posts", tags=["Posts"])

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)

@router.post("", response_model=PostSchema, status_code=201)
def create_post(post: PostCreate):
    """Create a new blog post."""
    post_id = str(uuid.uuid4())
    slug = post.slug or slugify(post.title)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check slug uniqueness
        cursor.execute("SELECT id FROM posts WHERE slug = ?", (slug,))
        if cursor.fetchone():
            slug = f"{slug}-{post_id[:8]}"
            
        cursor.execute(
            """
            INSERT INTO posts (id, title, slug, content, target_category, target_subject, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (post_id, post.title, slug, post.content, post.target_category, post.target_subject)
        )
        
    return PostSchema(
        id=post_id,
        title=post.title,
        slug=slug,
        content=post.content,
        target_category=post.target_category,
        target_subject=post.target_subject
    )

@router.get("", response_model=List[PostSchema])
def list_posts(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """List all blog posts."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, slug, content, target_category, target_subject, created_at
            FROM posts
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = cursor.fetchall()
        return [
            PostSchema(
                id=r["id"],
                title=r["title"],
                slug=r["slug"],
                content=r["content"],
                target_category=r["target_category"],
                target_subject=r["target_subject"],
                created_at=str(r["created_at"]) if r["created_at"] else None
            )
            for r in rows
        ]

@router.get("/{post_id}", response_model=PostSchema)
def get_post(post_id: str):
    """Retrieve post by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, slug, content, target_category, target_subject, created_at FROM posts WHERE id = ?", (post_id,))
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail=f"Post '{post_id}' not found")
        return PostSchema(
            id=r["id"],
            title=r["title"],
            slug=r["slug"],
            content=r["content"],
            target_category=r["target_category"],
            target_subject=r["target_subject"],
            created_at=str(r["created_at"]) if r["created_at"] else None
        )

@router.get("/{post_id}/suggestions", response_model=PostSuggestionsResponse)
def get_post_suggestions(post_id: str, limit: int = Query(5, ge=1, le=20)):
    """
    Retrieve ranked image suggestions for a blog post.
    All candidates pass through the Mismatch Guard safety layer.
    """
    try:
        return match_post_to_images(post_id=post_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
