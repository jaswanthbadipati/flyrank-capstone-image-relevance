"""Tests for Batch Background Processing, Retry Mechanisms, and Cost Tracking."""
import pytest
import tempfile
from pathlib import Path
from PIL import Image

from app.config import settings
from app.database import init_db, get_db
from app.services.cost_tracker import record_ai_cost, get_cost_analytics
from app.services.job_worker import create_batch_job, get_job_status, run_batch_ingest_worker, process_single_image_with_retries

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_cost_tracking_attribution():
    """PROBE 6: Test AI calls are attributed and tracked with accurate USD costs."""
    cost1 = record_ai_cost(
        operation="vision_classification",
        model_name="gemini-1.5-flash",
        prompt_tokens=1000,
        completion_tokens=200,
        duration_ms=150
    )
    assert cost1 > 0.0

    cost2 = record_ai_cost(
        operation="text_embedding",
        model_name="text-embedding-004",
        prompt_tokens=500,
        completion_tokens=0,
        duration_ms=45
    )
    assert cost2 > 0.0

    analytics = get_cost_analytics()
    assert analytics.total_calls >= 2
    assert analytics.total_tokens >= 1700
    assert "vision_classification" in analytics.breakdown_by_operation
    assert "text_embedding" in analytics.breakdown_by_operation

def test_batch_worker_processes_and_flags_low_confidence():
    """PROBE 1: Test batch worker processes images and flags blurry low-confidence files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # 1. Create a normal image
        normal_img = tmp_path / "red_fox_test.jpg"
        Image.new("RGB", (100, 100), color=(200, 80, 40)).save(normal_img)
        
        # 2. Create a blurry image
        blurry_img = tmp_path / "blurry_unknown_canine_test.jpg"
        Image.new("RGB", (100, 100), color=(100, 100, 100)).save(blurry_img)
        
        job_id = create_batch_job(job_type="batch_ingest", total_items=2)
        run_batch_ingest_worker(job_id, [normal_img, blurry_img])
        
        status = get_job_status(job_id)
        assert status.status == "completed"
        assert status.processed_items == 2
        assert status.failed_items == 0
        
        # Verify flagging in DB
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id, status, needs_review, flag_reason FROM images WHERE id = 'img_blurry_unknown_canine_test'")
            flagged = c.fetchone()
            assert flagged is not None
            assert flagged["needs_review"] == 1
            assert flagged["status"] == "flagged"
            assert "Low model confidence" in flagged["flag_reason"]
