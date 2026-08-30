"""API routes for image inventory and flagged image inspection."""
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models.schemas import ImageSchema, ImageMetadataSchema

router = APIRouter(prefix="/images", tags=["Images"])

@router.get("", response_model=List[ImageSchema])
def list_images(
    status: Optional[str] = Query(None, description="Filter by status ('pending', 'processed', 'flagged', 'failed')"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Retrieve list of images with extracted metadata."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                i.id, i.filename, i.filepath, i.source_url, i.license, i.status, i.needs_review, i.flag_reason, i.created_at,
                m.subject, m.category, m.attributes, m.caption, m.confidence, m.model_name, m.processed_at
            FROM images i
            LEFT JOIN image_metadata m ON i.id = m.image_id
        """
        params = []
        if status:
            query += " WHERE i.status = ?"
            params.append(status)
            
        query += " ORDER BY i.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            meta = None
            if r["subject"]:
                attrs = json.loads(r["attributes"]) if isinstance(r["attributes"], str) else r["attributes"]
                meta = ImageMetadataSchema(
                    image_id=r["id"],
                    subject=r["subject"],
                    category=r["category"],
                    attributes=attrs,
                    caption=r["caption"],
                    confidence=r["confidence"],
                    model_name=r["model_name"],
                    processed_at=str(r["processed_at"]) if r["processed_at"] else None
                )
            results.append(ImageSchema(
                id=r["id"],
                filename=r["filename"],
                filepath=r["filepath"],
                source_url=r["source_url"],
                license=r["license"],
                status=r["status"],
                needs_review=bool(r["needs_review"]),
                flag_reason=r["flag_reason"],
                created_at=str(r["created_at"]) if r["created_at"] else None,
                metadata=meta
            ))
        return results

@router.get("/flagged", response_model=List[ImageSchema])
def list_flagged_images():
    """Retrieve all images flagged for low confidence or errors requiring human review."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.id, i.filename, i.filepath, i.source_url, i.license, i.status, i.needs_review, i.flag_reason, i.created_at,
                m.subject, m.category, m.attributes, m.caption, m.confidence, m.model_name, m.processed_at
            FROM images i
            LEFT JOIN image_metadata m ON i.id = m.image_id
            WHERE i.needs_review = 1 OR i.status = 'flagged' OR i.status = 'failed'
            ORDER BY i.created_at DESC
        """)
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            meta = None
            if r["subject"]:
                attrs = json.loads(r["attributes"]) if isinstance(r["attributes"], str) else r["attributes"]
                meta = ImageMetadataSchema(
                    image_id=r["id"],
                    subject=r["subject"],
                    category=r["category"],
                    attributes=attrs,
                    caption=r["caption"],
                    confidence=r["confidence"],
                    model_name=r["model_name"],
                    processed_at=str(r["processed_at"]) if r["processed_at"] else None
                )
            results.append(ImageSchema(
                id=r["id"],
                filename=r["filename"],
                filepath=r["filepath"],
                source_url=r["source_url"],
                license=r["license"],
                status=r["status"],
                needs_review=bool(r["needs_review"]),
                flag_reason=r["flag_reason"],
                created_at=str(r["created_at"]) if r["created_at"] else None,
                metadata=meta
            ))
        return results

@router.get("/{image_id}", response_model=ImageSchema)
def get_image_detail(image_id: str):
    """Get single image metadata detail."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.id, i.filename, i.filepath, i.source_url, i.license, i.status, i.needs_review, i.flag_reason, i.created_at,
                m.subject, m.category, m.attributes, m.caption, m.confidence, m.model_name, m.processed_at
            FROM images i
            LEFT JOIN image_metadata m ON i.id = m.image_id
            WHERE i.id = ?
        """, (image_id,))
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail=f"Image with ID '{image_id}' not found")
            
        meta = None
        if r["subject"]:
            attrs = json.loads(r["attributes"]) if isinstance(r["attributes"], str) else r["attributes"]
            meta = ImageMetadataSchema(
                image_id=r["id"],
                subject=r["subject"],
                category=r["category"],
                attributes=attrs,
                caption=r["caption"],
                confidence=r["confidence"],
                model_name=r["model_name"],
                processed_at=str(r["processed_at"]) if r["processed_at"] else None
            )
        return ImageSchema(
            id=r["id"],
            filename=r["filename"],
            filepath=r["filepath"],
            source_url=r["source_url"],
            license=r["license"],
            status=r["status"],
            needs_review=bool(r["needs_review"]),
            flag_reason=r["flag_reason"],
            created_at=str(r["created_at"]) if r["created_at"] else None,
            metadata=meta
        )
