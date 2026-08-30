# Capstone Evidence & Acceptance Verification

This document provides concrete, reproducible proof for every requirement checkbox in Section 6 and each of the 6 Acceptance Probes.

---

## 1. Section 6 Requirements Checklist & Proofs

### [x] 1. Vision model produces structured output validated against a schema; invalid responses are never trusted.
- **Proof**: `tests/test_schema_validation.py` passes all schema enforcement checks. Pydantic `VisionOutput` rejects invalid fields, missing keys, and out-of-range confidence scores.
- **Code Reference**: `app/models/schemas.py:11-39` and `app/services/vision.py:165-175`.
- **Test Output**:
```text
tests/test_schema_validation.py::test_valid_vision_output_schema PASSED [ 84%]
tests/test_schema_validation.py::test_invalid_confidence_range PASSED   [ 89%]
tests/test_schema_validation.py::test_missing_required_fields PASSED    [ 94%]
tests/test_schema_validation.py::test_empty_string_validation PASSED    [100%]
```

---

### [x] 2. Low-confidence classifications are flagged instead of accepted.
- **Proof**: Blurry/indistinct images (`confidence < 0.70`) are stored with `needs_review=1`, `status='flagged'`, and `flag_reason`.
- **Console Proof**:
```text
Flagged images (needs_review=1): 2
 - img_blurry_unknown_canine_01 | status: flagged | reason: Low model confidence (0.48 < 0.70)
 - img_ambiguous_silhouette_02  | status: flagged | reason: Low model confidence (0.48 < 0.70)
```

---

### [x] 3. Images are processed through a batch background job with retries.
- **Proof**: `app/services/job_worker.py:run_batch_ingest_worker` processes corpus asynchronously, updates progress (`jobs` table), and retries with exponential backoff on errors.
- **Job Status Transcript**:
```json
{
  "job_id": "39b3a0dc-b55d-4b62-9c88-b3bb94ae1082",
  "job_type": "batch_ingest",
  "status": "completed",
  "total_items": 52,
  "processed_items": 52,
  "failed_items": 0,
  "retry_count": 0
}
```

---

### [x] 4. Vision and embedding costs are tracked per call.
- **Proof**: `cost_logs` table records `prompt_tokens`, `completion_tokens`, `total_tokens`, `cost_usd`, and `duration_ms` for every single AI call.
- **Analytics Log Output**:
```text
Cost logs count: 104 | total tokens: 18,733 | total cost USD: $0.002100
Breakdown:
 - vision_classification: 52 calls, 17,680 tokens, $0.002100 USD (avg: 1.2ms)
 - text_embedding: 52 calls, 1,053 tokens, $0.000000 USD (avg: 0.8ms)
```

---

### [x] 5. Image and post embeddings are stored; posts return ranked image suggestions.
- **Proof**: `GET /api/v1/posts/post_red_fox_behavior/suggestions` computes cosine similarity between stored vectors and returns ranked candidates.
- **API Response**:
```json
{
  "post_id": "post_red_fox_behavior",
  "post_title": "The Fascinating Behavior of Red Foxes in Temperate Forests",
  "status": "confident_match",
  "explanation": "Selected 'red fox' (similarity: 0.90, confidence: 0.95). Passed all taxonomic mismatch guard criteria.",
  "top_match": {
    "image_id": "img_red_fox_01",
    "filename": "red_fox_01.jpg",
    "caption": "A red fox (Vulpes vulpes) standing alert in a temperate autumn forest",
    "similarity_score": 0.9042,
    "confidence_score": 0.95,
    "guard_passed": true
  }
}
```

---

### [x] 6. Semantic matching works for equivalent concepts — "red fox" matches "Vulpes vulpes".
- **Proof**: Querying scientific post *"Taxonomic Adaptations of Vulpes vulpes Across Woodlands"* (eval_02) ranks `red_fox_01.jpg` #1 with score **0.85**.
- **Benchmark Row**:
```text
eval_02_vulpes_vulpes_scientific | Positive | red fox | red fox | 0.85 | [PASS] Top-1 Match (red_fox_01.jpg)
```

---

### [x] 7. The mismatch guard rejects incorrect recommendations — the wolf-on-a-fox-post scenario provably fails.
- **Proof**: Forcing `img_gray_wolf_01` on `post_red_fox_behavior` fails the guard with taxonomy rejection.
- **Verification Output**:
```text
Wolf Candidate Guard Passed: False
Rejection Reason: Semantic similarity score 0.01 below minimum acceptance threshold (0.60) | Subject taxonomy mismatch: post specifies 'red fox', but image depicts 'gray wolf'
Detailed Explanation: Pairing REJECTED by Mismatch Guard. Reason: Semantic similarity score 0.01 below minimum acceptance threshold (0.60) | Subject taxonomy mismatch: post specifies 'red fox', but image depicts 'gray wolf'.
```

---

### [x] 8. Rejections include a human-readable explanation.
- **Proof**: Rejection explanations describe the exact conflict:
  - `"Subject taxonomy mismatch: post specifies 'red fox', but image depicts 'gray wolf'"`
  - `"Vision classification confidence too low: 0.48 (required >= 0.70)"`
  - `"Semantic similarity score 0.10 below minimum acceptance threshold (0.60)"`

---

### [x] 9. When no image clears the bar, the system answers "no confident match" with reasons.
- **Proof**: Querying out-of-domain quantum post (`eval_15_quantum_unmatched`) returns `status="no_confident_match"` and `top_match=None`.
- **Transcript**:
```json
{
  "post_id": "eval_15_quantum_unmatched",
  "status": "no_confident_match",
  "explanation": "No confident match: Top candidate 'unidentified canine/animal' rejected: Vision classification confidence too low: 0.48 (required >= 0.70) | Semantic similarity score 0.10 below minimum acceptance threshold (0.60)",
  "top_match": null
}
```

---

### [x] 10. Database models for images, tags, embeddings, posts, suggestions, approvals/rejections with required indexes.
- **Proof**: `app/database.py` defines schemas and creates all 8 indexed tables: `images`, `image_metadata`, `embeddings`, `posts`, `suggestions`, `reviews`, `cost_logs`, `jobs`.

---

### [x] 11. API endpoints validated; the review workflow (approve / reject / inspect why) exists.
- **Proof**: `tests/test_api_endpoints.py::test_review_approval_and_rejection_workflow` passed.
  - `POST /api/v1/suggestions/{id}/approve` $\rightarrow$ sets status `approved` and logs review.
  - `POST /api/v1/suggestions/{id}/reject` $\rightarrow$ sets status `rejected` with editor notes.
  - `POST /api/v1/match/explain` $\rightarrow$ returns full `GuardBreakdown`.

---

### [x] 12. A small labeled evaluation dataset measures top-1 precision — the number is in your README.
- **Proof**: `eval/evaluate.py` benchmarks 16 samples. Measured Top-1 Precision = **100.0%** (matching `README.md`).

---

### [x] 13. README with architecture explanation and diagram; the required files present.
- **Files Present**:
  - `README.md`
  - `capstone.yaml`
  - `EVIDENCE.md`
  - `BUILDLOG.md`
  - `DESIGN.md`
  - `.env.example`
  - `LICENSE`

---

## 2. Live Acceptance Probes (All 6 Pass)

### PROBE 1 — Batch Ingestion & Low-Confidence Flagging
```bash
python scripts/seed_corpus.py
```
**Output**:
- 52 images processed.
- Blurry image (`blurry_unknown_canine_01.jpg`) flagged (`needs_review=1`, `status='flagged'`).

### PROBE 2 — Red Fox Query Ranks Fox #1
```bash
curl http://127.0.0.1:8000/api/v1/posts/post_red_fox_behavior/suggestions
```
**Output**: `red_fox_01.jpg` ranks first with similarity 0.90; wolf and dog score $\le 0.03$.

### PROBE 3 — Wolf Candidate on Fox Post Provably Rejected
```bash
curl -X POST http://127.0.0.1:8000/api/v1/match/explain -H "Content-Type: application/json" -d '{"post_id":"post_red_fox_behavior","image_id":"img_gray_wolf_01"}'
```
**Output**: `guard_passed: false`, `rejection_reason: "Subject taxonomy mismatch: post specifies 'red fox', but image depicts 'gray wolf'"`.

### PROBE 4 — Out-of-Domain Post Safely Refuses
```bash
curl http://127.0.0.1:8000/api/v1/posts/post_quantum_algorithms_out_of_domain/suggestions
```
**Output**: `status: "no_confident_match"`, `top_match: null`.

### PROBE 5 — Evaluation Precision Benchmark Matches README
```bash
python eval/evaluate.py
```
**Output**:
- Top-1 Precision: **100.0%** (14/14)
- Guard Rejection Accuracy: **100.0%** (2/2)
- False Positive Rate: **0.0%**

### PROBE 6 — Cost Log Attributed Per Call
```bash
curl http://127.0.0.1:8000/api/v1/analytics/costs
```
**Output**: Returns 104 tracked calls with prompt/completion token counts and USD attribution.
