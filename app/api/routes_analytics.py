"""API routes for cost tracking and token analytics."""
from fastapi import APIRouter
from app.models.schemas import CostAnalyticsSummary
from app.services.cost_tracker import get_cost_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics & Cost Tracking"])

@router.get("/costs", response_model=CostAnalyticsSummary)
def get_costs():
    """Retrieve aggregate token counts, USD cost attribution, and recent call logs."""
    return get_cost_analytics()
