# AI Usage Build Log (`BUILDLOG.md`)

## 1. Project Inception & Design Phase
- **Where AI Helped**:
  - Outlined the 4-tier Mismatch Guard safety layer architecture and drafted the initial Pydantic schema for `VisionOutput`.
  - Structured the SQLite schema with foreign key constraints, indexes, and audit tables.
- **Where AI Was Incomplete / Wrong**:
  - The initial AI draft suggested storing vectors directly in external SaaS vector databases (Pinecone / Qdrant) which violated the **$0 stack** and zero-external-dependency requirement.
- **What Was Changed**:
  - Designed an embedded SQLite + in-memory normalized NumPy cosine vector calculation engine that runs completely locally at $0 cost with sub-millisecond query latency.

---

## 2. Image Understanding & Schema Validation Pipeline
- **Where AI Helped**:
  - Implemented the Gemini Flash structured output generator with strict Pydantic model validation (`VisionOutput.model_validate(...)`).
  - Created the background batch worker with retry loops and exponential backoff.
- **Where AI Was Incomplete / Wrong**:
  - AI initially allowed missing optional fields on vision output, which risked trusting incomplete tags.
- **What Was Changed**:
  - Enforced `@field_validator("subject", "category", "caption")` on `VisionOutput` so empty strings or whitespace-only values immediately raise `ValidationError` and trigger retries or review flags.
  - Implemented deterministic flagging for images with `confidence < 0.70` (`needs_review=1`, `status="flagged"`).

---

## 3. The Mismatch Guard & Semantic Disambiguation
- **Where AI Helped**:
  - Designed the taxonomy mapping for subtle canine distinctions (*Red Fox* vs. *Fennec Fox* vs. *Gray Wolf* vs. *Golden Retriever Dog*).
  - Drafted the human-readable explanation generator for rejected pairings.
- **Where AI Was Incomplete / Wrong**:
  - In initial testing of the taxonomy guard, substring matching checked short aliases first (e.g. `"fox"` under red fox matched before `"fennec fox"` in `"fennec fox article"`, causing a false mismatch).
  - Post vector caching in the SQLite database caused stale vectors to persist when test posts were updated during benchmark runs.
  - The matching candidate ranker initially truncated candidates to `[:limit]` before passing them to the guard, causing valid matches ranked slightly lower in similarity to be missed if distractor candidates occupied top raw slots.
- **What Was Changed**:
  - Updated `extract_key_subject_from_text` and `find_candidate_canonical_subject` to sort all aliases by length descending (longest phrase matching first), eliminating collision.
  - Fixed candidate ranking in `matcher.py` to evaluate all candidate images against the guard first, then sort approved matches by similarity desc.
  - Added cache invalidation and fresh embedding generation on post updates.

---

## 4. Evaluation Benchmark & Production Hardening
- **Where AI Helped**:
  - Generated the 16-sample labeled evaluation benchmark (`eval/dataset.json`) and automated evaluation script (`eval/evaluate.py`).
  - Wrote the 19-test suite in `tests/` covering schema validation, guard refusal, batch worker retries, and REST endpoints.
- **Verification Result**:
  - Final benchmark achieved **100.0% Top-1 Precision** (14/14 positive test cases) and **100.0% Guard Rejection Accuracy** (2/2 negative test cases) with **0.0% False Positives**.
