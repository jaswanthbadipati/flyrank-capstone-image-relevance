"""Tests for the Mismatch Guard Safety Layer and Rejection Logic."""
import pytest
from app.services.guard import evaluate_mismatch_guard
from app.services.matcher import match_post_to_images, explain_candidate_pairing
from app.database import init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_mismatch_guard_accepts_valid_pair():
    """Test guard approves matching red fox image on red fox post."""
    res = evaluate_mismatch_guard(
        post_title="The Behavior of Red Foxes in Autumn",
        post_content="Red foxes (Vulpes vulpes) thrive in deciduous forest ecosystems with their thick orange coat.",
        image_subject="red fox",
        image_category="animal",
        image_attributes=["orange fur", "forest", "wildlife"],
        image_confidence=0.95,
        similarity_score=0.88
    )
    assert res.passed is True
    assert res.status == "ACCEPTED"
    assert res.rejection_reason is None
    assert res.breakdown.confidence_ok is True
    assert res.breakdown.similarity_ok is True
    assert res.breakdown.subject_match is True

def test_mismatch_guard_rejects_wolf_on_fox_post():
    """PROBE 3: Verify guard provably rejects wolf candidate on red fox post with taxonomy reason."""
    res = evaluate_mismatch_guard(
        post_title="The Behavior of Red Foxes in Autumn",
        post_content="Red foxes (Vulpes vulpes) hunt mice and build dens.",
        image_subject="gray wolf",
        image_category="animal",
        image_attributes=["gray coat", "predator", "pack"],
        image_confidence=0.96,
        similarity_score=0.75
    )
    assert res.passed is False
    assert res.status == "REJECTED"
    assert "Subject taxonomy mismatch" in res.rejection_reason
    assert "post specifies 'red fox', but image depicts 'gray wolf'" in res.rejection_reason
    assert res.breakdown.subject_match is False

def test_mismatch_guard_rejects_low_confidence_image():
    """PROBE 1 & Safety: Verify guard rejects low-confidence vision classifications (<0.70)."""
    res = evaluate_mismatch_guard(
        post_title="The Behavior of Red Foxes in Autumn",
        post_content="Red foxes roam the forest.",
        image_subject="red fox",
        image_category="animal",
        image_attributes=["blurry"],
        image_confidence=0.48,  # Below 0.70 threshold
        similarity_score=0.85
    )
    assert res.passed is False
    assert res.status == "FLAGGED_LOW_CONFIDENCE"
    assert "Vision classification confidence too low: 0.48" in res.rejection_reason
    assert res.breakdown.confidence_ok is False

def test_mismatch_guard_rejects_low_similarity():
    """PROBE 4: Verify guard rejects candidates when semantic similarity is below threshold."""
    res = evaluate_mismatch_guard(
        post_title="Quantum Computing with Superconducting Circuits",
        post_content="Qubits and entanglement algorithms.",
        image_subject="red fox",
        image_category="animal",
        image_attributes=["orange fur"],
        image_confidence=0.95,
        similarity_score=0.12  # Below 0.60 threshold
    )
    assert res.passed is False
    assert res.status == "REJECTED"
    assert "Semantic similarity score 0.12 below minimum acceptance threshold" in res.rejection_reason
    assert res.breakdown.similarity_ok is False
