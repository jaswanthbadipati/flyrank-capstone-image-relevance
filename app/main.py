"""FastAPI Application Main Entrypoint."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from app.config import settings
from app.database import init_db
from app.api import (
    images_router,
    posts_router,
    review_router,
    jobs_router,
    analytics_router,
    eval_router
)

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("flyrank.engine")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan context."""
    logger.info("Initializing database and storage directories...")
    init_db()
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Image Understanding & Content Matching Engine with Mismatch Guard safety layer.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(images_router, prefix=settings.API_V1_STR)
app.include_router(posts_router, prefix=settings.API_V1_STR)
app.include_router(review_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(eval_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    """System health and configuration check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def home():
    """Minimal admin table and status overview."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Image Matching Engine</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }
            h1 { color: #38bdf8; }
            .card { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155; }
            a { color: #38bdf8; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .badge { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; background: #0284c7; color: white; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 10px; border-bottom: 1px solid #334155; }
            th { color: #94a3b8; }
        </style>
    </head>
    <body>
        <h1>AI Image Understanding & Content Matching Engine</h1>
        <div class="card">
            <span class="badge">Operational</span>
            <p>Production AI reliability engine with a 4-tier <strong>Mismatch Guard</strong> safety layer.</p>
            <p>Access the interactive Swagger UI documentation at <a href="/docs">/docs</a> or OpenAPI specification at <a href="/openapi.json">/openapi.json</a>.</p>
        </div>
        <div class="card">
            <h2>Key Engine Endpoints</h2>
            <table>
                <thead>
                    <tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr>
                </thead>
                <tbody>
                    <tr><td>GET</td><td><a href="/api/v1/images">/api/v1/images</a></td><td>Image inventory & extracted structured metadata</td></tr>
                    <tr><td>GET</td><td><a href="/api/v1/images/flagged">/api/v1/images/flagged</a></td><td>Flagged low-confidence / review-required images</td></tr>
                    <tr><td>GET</td><td><a href="/api/v1/posts">/api/v1/posts</a></td><td>Blog post catalogue & target subjects</td></tr>
                    <tr><td>GET</td><td><a href="/api/v1/analytics/costs">/api/v1/analytics/costs</a></td><td>Token consumption & USD cost attribution</td></tr>
                    <tr><td>GET</td><td><a href="/api/v1/eval/run">/api/v1/eval/run</a></td><td>Live Top-1 precision evaluation benchmark</td></tr>
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
