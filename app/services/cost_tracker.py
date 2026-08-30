"""Cost tracking service for AI token usage and USD attribution."""
import uuid
import time
import logging
from typing import Dict, Any, List
from datetime import datetime
from app.database import get_db
from app.models.schemas import CostLogEntry, CostAnalyticsSummary

logger = logging.getLogger(__name__)

# Standard pricing model ($0 stack tracking)
# Gemini 1.5 Flash: $0.075 / 1M input tokens, $0.30 / 1M output tokens
# text-embedding-004: $0.00002 / 1k tokens ($0.02 / 1M tokens)
PRICING_PER_MILLION = {
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-flash": {"prompt": 0.075, "completion": 0.30},
    "text-embedding-004": {"prompt": 0.02, "completion": 0.00},
    "local-classifier": {"prompt": 0.00, "completion": 0.00},
    "local-embedding": {"prompt": 0.00, "completion": 0.00},
}

def calculate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate cost in USD based on model pricing."""
    pricing = PRICING_PER_MILLION.get(
        model_name.lower(),
        {"prompt": 0.075, "completion": 0.30}  # fallback default
    )
    cost = (prompt_tokens * pricing["prompt"] / 1_000_000.0) + (
        completion_tokens * pricing["completion"] / 1_000_000.0
    )
    return round(cost, 8)

def record_ai_cost(
    operation: str,
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: int
) -> float:
    """Record an AI call cost entry in the database."""
    total_tokens = prompt_tokens + completion_tokens
    cost_usd = calculate_cost(model_name, prompt_tokens, completion_tokens)
    log_id = str(uuid.uuid4())
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cost_logs (id, operation, model_name, prompt_tokens, completion_tokens, total_tokens, cost_usd, duration_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (log_id, operation, model_name, prompt_tokens, completion_tokens, total_tokens, cost_usd, duration_ms)
        )
    
    logger.info(f"AI Call Cost Logged [{operation}]: {total_tokens} tokens, ${cost_usd:.6f} USD ({duration_ms}ms)")
    return cost_usd

def get_cost_analytics() -> CostAnalyticsSummary:
    """Retrieve aggregate cost breakdown and recent logs."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Aggregates
        cursor.execute("""
            SELECT 
                COUNT(*) as total_calls,
                COALESCE(SUM(total_tokens), 0) as total_tokens,
                COALESCE(SUM(cost_usd), 0.0) as total_cost_usd
            FROM cost_logs
        """)
        totals = cursor.fetchone()
        
        # Operation breakdown
        cursor.execute("""
            SELECT 
                operation,
                COUNT(*) as calls,
                COALESCE(SUM(total_tokens), 0) as tokens,
                COALESCE(SUM(cost_usd), 0.0) as cost_usd,
                COALESCE(AVG(duration_ms), 0.0) as avg_duration_ms
            FROM cost_logs
            GROUP BY operation
        """)
        op_rows = cursor.fetchall()
        breakdown: Dict[str, Dict[str, Any]] = {}
        for row in op_rows:
            breakdown[row["operation"]] = {
                "calls": row["calls"],
                "total_tokens": row["tokens"],
                "total_cost_usd": round(row["cost_usd"], 6),
                "avg_duration_ms": round(row["avg_duration_ms"], 2)
            }
            
        # Recent logs
        cursor.execute("""
            SELECT id, operation, model_name, prompt_tokens, completion_tokens, total_tokens, cost_usd, duration_ms, created_at
            FROM cost_logs
            ORDER BY created_at DESC
            LIMIT 50
        """)
        recent_logs = [
            CostLogEntry(
                id=r["id"],
                operation=r["operation"],
                model_name=r["model_name"],
                prompt_tokens=r["prompt_tokens"],
                completion_tokens=r["completion_tokens"],
                total_tokens=r["total_tokens"],
                cost_usd=r["cost_usd"],
                duration_ms=r["duration_ms"],
                created_at=str(r["created_at"])
            )
            for r in cursor.fetchall()
        ]
        
    return CostAnalyticsSummary(
        total_calls=totals["total_calls"],
        total_tokens=totals["total_tokens"],
        total_cost_usd=round(totals["total_cost_usd"], 6),
        breakdown_by_operation=breakdown,
        recent_logs=recent_logs
    )
