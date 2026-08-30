"""Integration tests for all FastAPI REST endpoints and review workflows."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_health_check():
    """Test health check returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_list_images():
    """Test listing images from the catalogue."""
    response = client.get("/api/v1/images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_flagged_images():
    """PROBE 1: Test retrieving flagged low-confidence images."""
    response = client.get("/api/v1/images/flagged")
    assert response.status_code == 200
    flagged = response.json()
    assert isinstance(flagged, list)
    # Blurry canine from seed corpus should be flagged
    assert any(img["needs_review"] is True for img in flagged)

def test_create_post_and_get_suggestions():
    """PROBE 2: Test post creation and red fox matching first."""
    # 1. Create post
    post_payload = {
        "title": "Red Fox Denning Habits and Winter Survival",
        "content": "Red foxes (Vulpes vulpes) prepare their dens under snow and woodland trees during winter."
    }
    create_resp = client.post("/api/v1/posts", json=post_payload)
    assert create_resp.status_code == 201
    post_data = create_resp.json()
    post_id = post_data["id"]

    # 2. Query suggestions
    sugg_resp = client.get(f"/api/v1/posts/{post_id}/suggestions")
    assert sugg_resp.status_code == 200
    sugg_data = sugg_resp.json()
    assert sugg_data["status"] == "confident_match"
    assert sugg_data["top_match"] is not None
    assert "fox" in sugg_data["top_match"]["subject"].lower()
    assert sugg_data["top_match"]["guard_passed"] is True

def test_explain_candidate_match_endpoint():
    """PROBE 3: Test explain endpoint provably rejects forced wolf candidate."""
    # Create fox post
    post_resp = client.post("/api/v1/posts", json={
        "title": "Biology of the Red Fox",
        "content": "A detailed article about red foxes (Vulpes vulpes) in forest habitats."
    })
    post_id = post_resp.json()["id"]

    # Explain wolf pairing
    explain_resp = client.post("/api/v1/match/explain", json={
        "post_id": post_id,
        "image_id": "img_gray_wolf_01"
    })
    assert explain_resp.status_code == 200
    data = explain_resp.json()
    assert data["guard_passed"] is False
    assert "Subject taxonomy mismatch" in data["rejection_reason"]
    assert data["guard_breakdown"]["subject_match"] is False

def test_out_of_domain_post_rejection():
    """PROBE 4: Test out-of-domain post safely returns 'no_confident_match'."""
    post_resp = client.post("/api/v1/posts", json={
        "title": "Topological Quantum Field Theory in Solid State Physics",
        "content": "Non-abelian anyons and fractional quantum Hall states."
    })
    post_id = post_resp.json()["id"]

    sugg_resp = client.get(f"/api/v1/posts/{post_id}/suggestions")
    assert sugg_resp.status_code == 200
    sugg_data = sugg_resp.json()
    assert sugg_data["status"] == "no_confident_match"
    assert sugg_data["top_match"] is None
    assert "No confident match" in sugg_data["explanation"]

def test_review_approval_and_rejection_workflow():
    """Requirement 5: Test human review approve and reject actions."""
    # 1. Create post & get suggestions
    post_resp = client.post("/api/v1/posts", json={
        "title": "Grizzly Bears in Glacier National Park",
        "content": "Grizzly brown bears fishing and foraging in mountain streams."
    })
    post_id = post_resp.json()["id"]
    sugg_resp = client.get(f"/api/v1/posts/{post_id}/suggestions")
    sugg_id = sugg_resp.json()["top_match"]["id"]

    # 2. Approve suggestion
    app_resp = client.post(f"/api/v1/suggestions/{sugg_id}/approve", json={"action": "approve", "reviewer_notes": "Approved by senior editor"})
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "approved"

    # 3. Reject suggestion
    rej_resp = client.post(f"/api/v1/suggestions/{sugg_id}/reject", json={"action": "reject", "reviewer_notes": "Re-pairing with alternative photo"})
    assert rej_resp.status_code == 200
    assert rej_resp.json()["status"] == "rejected"

def test_cost_analytics_endpoint():
    """PROBE 6: Test cost analytics endpoint returns breakdown."""
    response = client.get("/api/v1/analytics/costs")
    assert response.status_code == 200
    data = response.json()
    assert "total_calls" in data
    assert "total_cost_usd" in data
    assert "breakdown_by_operation" in data

def test_evaluation_benchmark_endpoint():
    """PROBE 5: Test eval endpoint runs benchmark and reports metrics."""
    response = client.get("/api/v1/eval/run")
    assert response.status_code == 200
    data = response.json()
    assert data["top1_precision"] >= 90.0
    assert data["guard_rejection_accuracy"] == 100.0
