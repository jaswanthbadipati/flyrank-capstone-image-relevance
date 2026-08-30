"""Database persistence layer with SQLite."""
import sqlite3
import json
import logging
from contextlib import contextmanager
from typing import Generator
from app.config import settings

logger = logging.getLogger(__name__)

def get_db_connection() -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database sessions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database tables and create required indexes."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Images table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                source_url TEXT,
                license TEXT NOT NULL DEFAULT 'Unsplash / Pexels Free License',
                status TEXT NOT NULL DEFAULT 'pending',
                needs_review INTEGER NOT NULL DEFAULT 0,
                flag_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_status ON images(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_needs_review ON images(needs_review);")

        # 2. Image Metadata table (structured vision output)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_metadata (
                image_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                category TEXT NOT NULL,
                attributes TEXT NOT NULL, -- JSON array of strings
                caption TEXT NOT NULL,
                confidence REAL NOT NULL,
                raw_response TEXT,
                model_name TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
            );
        """)

        # 3. Vector Embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL, -- 'image' or 'post'
                entity_id TEXT NOT NULL,
                embedding_json TEXT NOT NULL, -- JSON float array
                dimension INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_entity ON embeddings(entity_type, entity_id);")

        # 4. Blog Posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                target_category TEXT,
                target_subject TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);")

        # 5. Matching Suggestions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL,
                image_id TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                guard_passed INTEGER NOT NULL,
                rejection_reason TEXT,
                guard_breakdown TEXT, -- JSON diagnostic detail
                status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_suggestions_post ON suggestions(post_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_suggestions_image ON suggestions(image_id);")

        # 6. Human Review Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY,
                suggestion_id TEXT NOT NULL,
                action TEXT NOT NULL, -- 'approve', 'reject'
                reviewer_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (suggestion_id) REFERENCES suggestions(id) ON DELETE CASCADE
            );
        """)

        # 7. AI Cost & Token Audit Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_logs (
                id TEXT PRIMARY KEY,
                operation TEXT NOT NULL, -- 'vision_classification', 'text_embedding'
                model_name TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                duration_ms INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_logs_operation ON cost_logs(operation);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_logs_created ON cost_logs(created_at);")

        # 8. Batch Background Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued', -- 'queued', 'running', 'completed', 'failed'
                total_items INTEGER DEFAULT 0,
                processed_items INTEGER DEFAULT 0,
                failed_items INTEGER DEFAULT 0,
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            );
        """)
        
    logger.info("Database schema initialized successfully.")
