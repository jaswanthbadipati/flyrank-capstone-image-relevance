"""API routes for evaluation benchmarking."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import EvalRunResponse

router = APIRouter(prefix="/eval", tags=["Evaluation"])

@router.get("/run", response_model=EvalRunResponse)
def run_eval_endpoint():
    """
    Run evaluation benchmark against ground-truth dataset and return top-1 precision and safety metrics.
    """
    try:
        from eval.evaluate import run_benchmark
        return run_benchmark()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation run failed: {str(e)}")
