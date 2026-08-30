"""Pydantic schema definitions for request/response validation and structured AI outputs."""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

# ==========================================================
# 1. Vision Structured Output Schema (Requirement 1 & Schema Validation)
# ==========================================================
class VisionOutput(BaseModel):
    """Strict schema for multimodal vision model extraction."""
    subject: str = Field(
        ...,
        description="The primary identified entity/subject (e.g., 'red fox', 'gray wolf', 'golden retriever')"
    )
    category: str = Field(
        ...,
        description="The high-level taxonomic or domain category (e.g., 'animal', 'canine', 'landscape', 'technology')"
    )
    attributes: List[str] = Field(
        default_factory=list,
        description="Descriptive tags, physical traits, colors, habitat context"
    )
    caption: str = Field(
        ...,
        description="A rich, objective natural language caption describing the scene"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Self-assessed model confidence score between 0.0 and 1.0"
    )

    @field_validator("subject", "category", "caption")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


# ==========================================================
# 2. Image Schemas
# ==========================================================
class ImageMetadataSchema(BaseModel):
    image_id: str
    subject: str
    category: str
    attributes: List[str]
    caption: str
    confidence: float
    model_name: str
    processed_at: Optional[str] = None

class ImageSchema(BaseModel):
    id: str
    filename: str
    filepath: str
    source_url: Optional[str] = None
    license: str
    status: str
    needs_review: bool
    flag_reason: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Optional[ImageMetadataSchema] = None

class ImageUploadResponse(BaseModel):
    message: str
    image: ImageSchema


# ==========================================================
# 3. Post Schemas
# ==========================================================
class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=250)
    slug: Optional[str] = None
    content: str = Field(..., min_length=10)
    target_category: Optional[str] = None
    target_subject: Optional[str] = None

class PostSchema(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    target_category: Optional[str] = None
    target_subject: Optional[str] = None
    created_at: Optional[str] = None


# ==========================================================
# 4. Mismatch Guard & Suggestion Schemas (Requirement 3 & 4)
# ==========================================================
class GuardBreakdown(BaseModel):
    confidence_ok: bool
    similarity_ok: bool
    category_ok: bool
    subject_match: bool
    confidence_score: float
    similarity_score: float
    rejection_reasons: List[str] = Field(default_factory=list)

class MismatchGuardResult(BaseModel):
    passed: bool
    status: Literal["ACCEPTED", "REJECTED", "FLAGGED_LOW_CONFIDENCE"]
    rejection_reason: Optional[str] = None
    confidence_score: float
    similarity_score: float
    breakdown: GuardBreakdown

class SuggestionItem(BaseModel):
    id: Optional[str] = None
    image_id: str
    filename: str
    caption: str
    subject: str
    category: str
    attributes: List[str] = Field(default_factory=list)
    similarity_score: float
    confidence_score: float
    guard_passed: bool
    rejection_reason: Optional[str] = None
    guard_breakdown: Optional[Dict[str, Any]] = None

class PostSuggestionsResponse(BaseModel):
    post_id: str
    post_title: str
    status: Literal["confident_match", "no_confident_match"]
    explanation: str
    top_match: Optional[SuggestionItem] = None
    candidates: List[SuggestionItem] = Field(default_factory=list)

class ExplainMatchRequest(BaseModel):
    post_id: str
    image_id: str

class ExplainMatchResponse(BaseModel):
    post_id: str
    post_title: str
    image_id: str
    image_filename: str
    similarity_score: float
    image_confidence: float
    guard_passed: bool
    rejection_reason: Optional[str] = None
    detailed_explanation: str
    guard_breakdown: GuardBreakdown


# ==========================================================
# 5. Human-in-the-Loop Review Schemas (Requirement 5)
# ==========================================================
class ReviewActionRequest(BaseModel):
    action: Literal["approve", "reject"]
    reviewer_notes: Optional[str] = None

class ReviewActionResponse(BaseModel):
    suggestion_id: str
    status: str
    action_recorded: str
    notes: Optional[str] = None
    reviewed_at: str


# ==========================================================
# 6. Cost Tracking & Job Schemas (Requirement 4 & Background)
# ==========================================================
class CostLogEntry(BaseModel):
    id: str
    operation: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    duration_ms: int
    created_at: str

class CostAnalyticsSummary(BaseModel):
    total_calls: int
    total_tokens: int
    total_cost_usd: float
    breakdown_by_operation: Dict[str, Dict[str, Any]]
    recent_logs: List[CostLogEntry]

class BatchJobResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    total_items: int
    processed_items: int
    failed_items: int
    retry_count: int
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ==========================================================
# 7. Evaluation Benchmark Schema
# ==========================================================
class EvalResultItem(BaseModel):
    post_id: str
    post_title: str
    expected_image_id: Optional[str]
    actual_image_id: Optional[str]
    actual_status: str
    top1_correct: bool
    guard_rejection_correct: bool
    similarity_score: float
    notes: str

class EvalRunResponse(BaseModel):
    total_eval_samples: int
    positive_samples: int
    negative_distractor_samples: int
    top1_precision: float
    guard_rejection_accuracy: float
    false_positive_rate: float
    timestamp: str
    results: List[EvalResultItem]
