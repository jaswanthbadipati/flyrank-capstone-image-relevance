"""Matching engine service: Combines vector similarity retrieval with Mismatch Guard safety checks."""
import json
import uuid
import logging
from typing import List, Optional, Tuple, Dict, Any

from app.config import settings
from app.database import get_db
from app.services.embedding import generate_embedding, cosine_similarity
from app.services.guard import evaluate_mismatch_guard
from app.models.schemas import (
    SuggestionItem,
    PostSuggestionsResponse,
    ExplainMatchResponse,
    GuardBreakdown
)

logger = logging.getLogger(__name__)

def match_post_to_images(post_id: str, limit: int = 5) -> PostSuggestionsResponse:
    """
    Rank all available images for a given blog post, evaluate them with the Mismatch Guard,
    and persist suggestions.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Fetch Post
        cursor.execute("SELECT id, title, slug, content FROM posts WHERE id = ?", (post_id,))
        post_row = cursor.fetchone()
        if not post_row:
            raise ValueError(f"Post with ID {post_id} not found")
            
        post_title = post_row["title"]
        post_content = post_row["content"]
        
        # 2. Get or generate post embedding
        cursor.execute("SELECT embedding_json FROM embeddings WHERE entity_type = 'post' AND entity_id = ?", (post_id,))
        post_emb_row = cursor.fetchone()
        if post_emb_row:
            post_vec = json.loads(post_emb_row["embedding_json"])
        else:
            combined_text = f"{post_title}. {post_content}"
            post_vec, cost_usd, model_name = generate_embedding(combined_text)
            cursor.execute(
                """
                INSERT OR REPLACE INTO embeddings (id, entity_type, entity_id, embedding_json, dimension, model_name)
                VALUES (?, 'post', ?, ?, ?, ?)
                """,
                (str(uuid.uuid4()), post_id, json.dumps(post_vec), len(post_vec), model_name)
            )

        # 3. Fetch all processed images with metadata and embeddings
        cursor.execute("""
            SELECT 
                i.id as image_id,
                i.filename,
                i.filepath,
                i.status,
                i.needs_review,
                m.subject,
                m.category,
                m.attributes,
                m.caption,
                m.confidence,
                e.embedding_json
            FROM images i
            JOIN image_metadata m ON i.id = m.image_id
            JOIN embeddings e ON i.id = e.entity_id AND e.entity_type = 'image'
        """)
        image_rows = cursor.fetchall()

    if not image_rows:
        return PostSuggestionsResponse(
            post_id=post_id,
            post_title=post_title,
            status="no_confident_match",
            explanation="No processed image records exist in the vector database.",
            top_match=None,
            candidates=[]
        )

    # 4. Score all candidates with cosine similarity and evaluate against Mismatch Guard
    all_evaluated = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for r in image_rows:
            img_vec = json.loads(r["embedding_json"])
            sim_score = cosine_similarity(post_vec, img_vec)
            attrs = json.loads(r["attributes"]) if isinstance(r["attributes"], str) else r["attributes"]
            
            # Run Mismatch Guard
            guard_res = evaluate_mismatch_guard(
                post_title=post_title,
                post_content=post_content,
                image_subject=r["subject"],
                image_category=r["category"],
                image_attributes=attrs,
                image_confidence=r["confidence"],
                similarity_score=sim_score
            )
            
            suggestion_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT OR REPLACE INTO suggestions (
                    id, post_id, image_id, similarity_score, guard_passed,
                    rejection_reason, guard_breakdown, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    suggestion_id,
                    post_id,
                    r["image_id"],
                    round(sim_score, 4),
                    1 if guard_res.passed else 0,
                    guard_res.rejection_reason,
                    json.dumps(guard_res.breakdown.model_dump())
                )
            )
            
            item = SuggestionItem(
                id=suggestion_id,
                image_id=r["image_id"],
                filename=r["filename"],
                caption=r["caption"],
                subject=r["subject"],
                category=r["category"],
                attributes=attrs,
                similarity_score=round(sim_score, 4),
                confidence_score=round(r["confidence"], 4),
                guard_passed=guard_res.passed,
                rejection_reason=guard_res.rejection_reason,
                guard_breakdown=guard_res.breakdown.model_dump()
            )
            all_evaluated.append(item)

    # 5. Sort candidates: approved candidates first sorted by similarity desc, then rejected sorted by similarity desc
    passed_candidates = [c for c in all_evaluated if c.guard_passed]
    passed_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
    
    failed_candidates = [c for c in all_evaluated if not c.guard_passed]
    failed_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
    
    top_approved_match = passed_candidates[0] if passed_candidates else None
    
    # Combined top candidates for API response
    display_candidates = (passed_candidates + failed_candidates)[:limit]

    # 6. Formulate response
    if top_approved_match:
        return PostSuggestionsResponse(
            post_id=post_id,
            post_title=post_title,
            status="confident_match",
            explanation=f"Selected '{top_approved_match.subject}' (similarity: {top_approved_match.similarity_score:.2f}, confidence: {top_approved_match.confidence_score:.2f}). Passed all taxonomic mismatch guard criteria.",
            top_match=top_approved_match,
            candidates=display_candidates
        )
    else:
        if failed_candidates:
            best_candidate = failed_candidates[0]
            reason = best_candidate.rejection_reason or "Candidates failed similarity or safety thresholds."
            detail = f"Top candidate '{best_candidate.subject}' rejected: {reason}"
        else:
            detail = "No candidate images cleared the minimum similarity threshold."
            
        return PostSuggestionsResponse(
            post_id=post_id,
            post_title=post_title,
            status="no_confident_match",
            explanation=f"No confident match: {detail}",
            top_match=None,
            candidates=display_candidates
        )

def explain_candidate_pairing(post_id: str, image_id: str) -> ExplainMatchResponse:
    """
    Detailed inspection endpoint for evaluating a specific candidate image against a post.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Fetch post
        cursor.execute("SELECT id, title, content FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        if not post:
            raise ValueError(f"Post ID {post_id} not found")
            
        # Fetch image
        cursor.execute("""
            SELECT i.id, i.filename, m.subject, m.category, m.attributes, m.caption, m.confidence, e.embedding_json
            FROM images i
            JOIN image_metadata m ON i.id = m.image_id
            JOIN embeddings e ON i.id = e.entity_id AND e.entity_type = 'image'
            WHERE i.id = ?
        """, (image_id,))
        img = cursor.fetchone()
        if not img:
            raise ValueError(f"Image ID {image_id} not found or not processed")
            
        # Get post vector
        cursor.execute("SELECT embedding_json FROM embeddings WHERE entity_type = 'post' AND entity_id = ?", (post_id,))
        post_emb_row = cursor.fetchone()
        if post_emb_row:
            post_vec = json.loads(post_emb_row["embedding_json"])
        else:
            post_vec, _, _ = generate_embedding(f"{post['title']}. {post['content']}")
            
        img_vec = json.loads(img["embedding_json"])
        sim_score = cosine_similarity(post_vec, img_vec)
        attrs = json.loads(img["attributes"]) if isinstance(img["attributes"], str) else img["attributes"]
        
        guard_res = evaluate_mismatch_guard(
            post_title=post["title"],
            post_content=post["content"],
            image_subject=img["subject"],
            image_category=img["category"],
            image_attributes=attrs,
            image_confidence=img["confidence"],
            similarity_score=sim_score
        )
        
        if guard_res.passed:
            detailed_exp = f"Pairing APPROVED. Candidate image depicts '{img['subject']}' which aligns with post topic '{post['title']}' with similarity {sim_score:.2f} and confidence {img['confidence']:.2f}."
        else:
            detailed_exp = f"Pairing REJECTED by Mismatch Guard. Reason: {guard_res.rejection_reason}."
            
        return ExplainMatchResponse(
            post_id=post["id"],
            post_title=post["title"],
            image_id=img["id"],
            image_filename=img["filename"],
            similarity_score=round(sim_score, 4),
            image_confidence=round(img["confidence"], 4),
            guard_passed=guard_res.passed,
            rejection_reason=guard_res.rejection_reason,
            detailed_explanation=detailed_exp,
            guard_breakdown=guard_res.breakdown
        )
