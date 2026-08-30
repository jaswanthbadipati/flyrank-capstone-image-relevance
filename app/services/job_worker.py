"""Background batch processing service with retries, exponential backoff, progress tracking, and cost attribution."""
import asyncio
import time
import json
import uuid
import logging
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.database import get_db
from app.models.schemas import BatchJobResponse
from app.services.vision import process_image_vision
from app.services.embedding import generate_embedding

logger = logging.getLogger(__name__)

def create_batch_job(job_type: str = "batch_ingest", total_items: int = 0) -> str:
    """Create a new job entry in the database."""
    job_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs (id, job_type, status, total_items, processed_items, failed_items, retry_count, started_at)
            VALUES (?, ?, 'queued', ?, 0, 0, 0, CURRENT_TIMESTAMP)
            """,
            (job_id, job_type, total_items)
        )
    return job_id

def get_job_status(job_id: str) -> Optional[BatchJobResponse]:
    """Fetch status for a specific job."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, job_type, status, total_items, processed_items, failed_items, retry_count, error_message, started_at, completed_at
            FROM jobs
            WHERE id = ?
        """, (job_id,))
        row = cursor.fetchone()
        if not row:
            return None
            
        return BatchJobResponse(
            job_id=row["id"],
            job_type=row["job_type"],
            status=row["status"],
            total_items=row["total_items"],
            processed_items=row["processed_items"],
            failed_items=row["failed_items"],
            retry_count=row["retry_count"],
            error_message=row["error_message"],
            started_at=str(row["started_at"]) if row["started_at"] else None,
            completed_at=str(row["completed_at"]) if row["completed_at"] else None
        )

def process_single_image_with_retries(image_path: Path, image_id: Optional[str] = None) -> bool:
    """
    Process an individual image: extract vision metadata, enforce validation,
    flag low confidence, generate embeddings, and store records.
    Includes retry loop with backoff.
    """
    if not image_id:
        image_id = str(uuid.uuid4())
        
    retries = 0
    max_retries = settings.MAX_BATCH_RETRIES
    backoff = settings.RETRY_BACKOFF_SECONDS
    
    while retries <= max_retries:
        try:
            # 1. Vision structured extraction & validation
            vision_out, cost_usd, model_name, raw_dict = process_image_vision(image_path)
            
            # Determine review flag
            is_low_conf = vision_out.confidence < settings.MIN_CONFIDENCE_THRESHOLD
            status = "flagged" if is_low_conf else "processed"
            flag_reason = f"Low model confidence ({vision_out.confidence:.2f} < {settings.MIN_CONFIDENCE_THRESHOLD:.2f})" if is_low_conf else None
            needs_review = 1 if is_low_conf else 0
            
            # 2. Persist image and metadata
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO images (id, filename, filepath, license, status, needs_review, flag_reason, created_at)
                    VALUES (?, ?, ?, 'Unsplash / Pexels Licensed Free', ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (image_id, image_path.name, str(image_path), status, needs_review, flag_reason)
                )
                
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO image_metadata (image_id, subject, category, attributes, caption, confidence, raw_response, model_name, processed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        image_id,
                        vision_out.subject,
                        vision_out.category,
                        json.dumps(vision_out.attributes),
                        vision_out.caption,
                        vision_out.confidence,
                        json.dumps(raw_dict),
                        model_name
                    )
                )

            # 3. Generate and store caption embedding
            embed_text = f"{vision_out.subject}. {vision_out.caption}. {' '.join(vision_out.attributes)}"
            vec, emb_cost, emb_model = generate_embedding(embed_text)
            
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO embeddings (id, entity_type, entity_id, embedding_json, dimension, model_name, created_at)
                    VALUES (?, 'image', ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (str(uuid.uuid4()), image_id, json.dumps(vec), len(vec), emb_model)
                )
                
            logger.info(f"Successfully processed image: {image_path.name} (status: {status}, conf: {vision_out.confidence:.2f})")
            return True
            
        except Exception as e:
            retries += 1
            logger.warning(f"Error processing {image_path.name} (attempt {retries}/{max_retries + 1}): {e}")
            if retries <= max_retries:
                time.sleep(backoff * (2 ** (retries - 1)))
            else:
                # Mark as failed in DB
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO images (id, filename, filepath, license, status, needs_review, flag_reason, created_at)
                        VALUES (?, ?, ?, 'Unsplash / Pexels Licensed Free', 'failed', 1, ?, CURRENT_TIMESTAMP)
                        """,
                        (image_id, image_path.name, str(image_path), f"Processing failed after {max_retries} retries: {str(e)}")
                    )
                return False
                
    return False

def run_batch_ingest_worker(job_id: str, image_paths: List[Path]):
    """
    Executes the batch processing background job.
    Updates progress and metrics in SQLite.
    """
    logger.info(f"Starting batch worker for Job {job_id} ({len(image_paths)} images)")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE jobs SET status = 'running', total_items = ? WHERE id = ?", (len(image_paths), job_id))

    processed_count = 0
    failed_count = 0
    
    for idx, img_path in enumerate(image_paths):
        # Generate predictable ID or UUID based on filename
        img_id = f"img_{img_path.stem}"
        success = process_single_image_with_retries(img_path, image_id=img_id)
        
        if success:
            processed_count += 1
        else:
            failed_count += 1
            
        # Update progress
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE jobs 
                SET processed_items = ?, failed_items = ?
                WHERE id = ?
                """,
                (processed_count, failed_count, job_id)
            )

    # Mark completed
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE jobs 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (job_id,)
        )
    logger.info(f"Batch Job {job_id} completed: {processed_count} processed, {failed_count} failed.")
