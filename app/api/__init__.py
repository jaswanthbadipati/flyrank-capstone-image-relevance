"""API Routers Package"""
from app.api.routes_images import router as images_router
from app.api.routes_posts import router as posts_router
from app.api.routes_review import router as review_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_eval import router as eval_router

__all__ = [
    "images_router",
    "posts_router",
    "review_router",
    "jobs_router",
    "analytics_router",
    "eval_router",
]
