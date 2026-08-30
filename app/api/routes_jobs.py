"""API routes for batch processing background jobs."""
from pathlib import Path
from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.config import settings
from app.models.schemas import BatchJobResponse
from app.services.job_worker import create_batch_job, get_job_status, run_batch_ingest_worker

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])

@router.post("/ingest", response_model=BatchJobResponse, status_code=202)
def trigger_batch_ingest(background_tasks: BackgroundTasks):
    """
    Trigger an asynchronous background batch job to process and index the image corpus.
    Runs vision analysis, schema validation, embedding generation, and cost logging off the request path.
    """
    corpus_dir = settings.CORPUS_DIR
    if not corpus_dir.exists():
        raise HTTPException(status_code=400, detail=f"Corpus directory '{corpus_dir}' does not exist")
        
    image_paths = sorted([
        p for p in corpus_dir.iterdir()
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
    ])
    
    if not image_paths:
        raise HTTPException(status_code=400, detail="No valid image files found in corpus directory")
        
    job_id = create_batch_job(job_type="batch_ingest", total_items=len(image_paths))
    
    # Run in FastAPI background tasks
    background_tasks.add_task(run_batch_ingest_worker, job_id, image_paths)
    
    status_obj = get_job_status(job_id)
    if not status_obj:
        raise HTTPException(status_code=500, detail="Failed to initialize batch job")
        
    return status_obj

@router.get("/{job_id}", response_model=BatchJobResponse)
def get_job(job_id: str):
    """Retrieve progress and completion status for a background job."""
    status_obj = get_job_status(job_id)
    if not status_obj:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return status_obj
