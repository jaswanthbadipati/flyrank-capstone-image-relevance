# AI Image Understanding & Content Matching Engine

> **Production AI Reliability**: A multimodal vision and semantic matching system with a 4-tier **Mismatch Guard** safety layer. Ensures blog posts receive the exact right image (a red fox gets a red fox, never a wolf), surfaces high-confidence matches, and safely rejects ambiguous or low-similarity candidates with human-readable explanations.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange.svg)](https://docs.pydantic.dev/)
[![Evaluation Top-1 Precision](https://img.shields.io/badge/Top--1%20Precision-100.0%25-brightgreen.svg)]()
[![Cost](https://img.shields.io/badge/%240%20Stack-No%20Credit%20Card-success.svg)]()

---

## 1. Architecture Overview

The system operates via two parallel embedding streams that meet at the similarity ranking step. Every candidate must pass through the **Mismatch Guard** safety funnel before human editors or publishing workflows ever see it.

```
+----------------------------------------------------------------------------------------------------+
|                                         IMAGE INGESTION STREAM                                     |
|  Image Corpus (~50 images)                                                                         |
|      │                                                                                             |
|      ▼ (Async Batch Worker + Exponential Backoff Retries)                                          |
|  Vision Model (Gemini 1.5 Flash / Local Simulator)                                                 |
|      │                                                                                             |
|      ▼ (Pydantic Schema Validation)                                                                |
|  Structured Output: { subject, category, attributes, caption, confidence }                         |
|      │                                                                                             |
|      ├─► Low Confidence (< 0.70)? ──► [FLAGGED FOR REVIEW] (never silently accepted)              |
|      ▼                                                                                             |
|  Embeddings Generator ──► [image_vectors table (128-d / 768-d)]                                    |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
|                                          POST MATCHING STREAM                                      |
|  Blog Post Content & Title ──► Embeddings Generator ──► [post_vectors]                             |
|                                                                                                    |
|  GET /api/v1/posts/:id/suggestions                                                                 |
|      │                                                                                             |
|      ▼                                                                                             |
|  Cosine Similarity Search (post_vector × image_vectors)                                            |
|      │                                                                                             |
|      ▼                                                                                             |
|  THE MISMATCH GUARD SAFETY LAYER:                                                                  |
|      ├── 1. Vision Confidence Gate (confidence >= 0.70)                                            |
|      ├── 2. Minimum Similarity Threshold (similarity >= 0.60)                                      |
|      ├── 3. Taxonomic & Subject Disambiguation (e.g. Red Fox vs. Gray Wolf vs. Dog)               |
|      └── 4. Cross-Domain Category Filtering                                                        |
|      │                                                                                             |
|      ├──► PASS ──► "confident_match" (Ranked suggestions with scores and tags)                     |
|      └──► FAIL ──► "no_confident_match" (Safe refusal with human-readable reason)                  |
|                                                                                                    |
|  Human-in-the-Loop Review API: Approve / Reject / Inspect Why (/api/v1/match/explain)              |
|  Per-Call Cost & Token Audit Log (/api/v1/analytics/costs)                                         |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Key Features

1. **Multimodal Structured Extraction**: Enforces strict Pydantic schema validation (`VisionOutput`) on vision model responses. Invalid outputs are rejected and retried with backoff.
2. **Low-Confidence Flagging**: Any image with classification confidence $< 0.70$ (e.g., blurry photos, indistinct silhouettes) is automatically flagged (`needs_review=1`, `status="flagged"`).
3. **Semantic Concept Matching**: Encodes captions and articles in a shared semantic vector space. Equivalent concepts like *"red fox"* and *"Vulpes vulpes"* match seamlessly.
4. **The Mismatch Guard**:
   - Defends the critical **Fox vs. Wolf vs. Dog** taxonomic boundary.
   - Forcing a wolf photo onto a fox article provably fails with: `"Subject taxonomy mismatch: post specifies 'red fox', but image depicts 'gray wolf'"`.
   - Rejects out-of-domain articles with a safe `"no_confident_match"` status and diagnostic explanations.
5. **Background Batch Processing**: Off-request-path batch ingestion queue with exponential backoff retries and live progress tracking.
6. **Per-Call Cost Tracking**: Tracks prompt tokens, completion tokens, duration (ms), and USD cost for every single vision and embedding invocation.
7. **Human-in-the-Loop Review Workflow**: REST endpoints for editorial approval (`/approve`), rejection with notes (`/reject`), and deep inspection (`/explain`).

---

## 3. Evaluation & Benchmark Results

The system is evaluated against a labeled benchmark dataset (`eval/dataset.json`) containing 16 test cases (positive concept matches, scientific synonyms, distractors, out-of-domain articles, and forced negative pairings).

| Metric | Result | Target Benchmark | Status |
|---|---|---|---|
| **Top-1 Precision** | **100.0%** (14/14) | $\ge 90.0\%$ | **PASS** |
| **Guard Rejection Accuracy** | **100.0%** (2/2) | $100.0\%$ | **PASS** |
| **False Positive Rate** | **0.0%** | $\le 5.0\%$ | **PASS** |
| **Ambiguous Image Flagging** | **100.0%** (2/2) | $100.0\%$ | **PASS** |

To reproduce the benchmark:
```bash
python eval/evaluate.py
```

---

## 4. The $0 Stack

Every tool and dependency in this project is 100% free with no credit card required:
- **Language & Framework**: Python 3.10+ / FastAPI / Uvicorn
- **Validation**: Pydantic v2 (`VisionOutput`, `PostSchema`, `MismatchGuardResult`)
- **Database**: SQLite with WAL mode & indexed tables (zero external daemon needed)
- **Vision Model**: Gemini 1.5 Flash (Google AI Studio free tier) or local offline classifier
- **Embeddings**: Gemini `text-embedding-004` or local semantic vector projector (128-d / L2 normalized)
- **Image Corpus**: ~50 licensed-free wildlife and domain images (Unsplash / Pexels license)

---

## 5. Quick Start & Execution

### 5.1 Installation
```bash
# Clone repository
git clone https://github.com/your-username/flyrank-capstone-image-relevance.git
cd flyrank-capstone-image-relevance

# Install dependencies
pip install -r requirements.txt
```

### 5.2 Environment Setup
Copy the example environment configuration:
```bash
cp .env.example .env
```
*(Default settings run in deterministic `offline` mode. To enable live Gemini API, set `AI_PROVIDER=gemini` and provide your `GEMINI_API_KEY`.)*

### 5.3 Seed Database & Process 50-Image Corpus
```bash
python scripts/seed_corpus.py
```

### 5.4 Run Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Admin Overview: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 5.5 Run Automated Test Suite
```bash
python -m pytest -v
```

---

## 6. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/jobs/ingest` | Trigger async batch processing job on corpus |
| `GET` | `/api/v1/jobs/{id}` | Poll background job progress and status |
| `GET` | `/api/v1/images` | List all ingested images with extracted metadata |
| `GET` | `/api/v1/images/flagged` | List low-confidence / review-required images |
| `POST` | `/api/v1/posts` | Create a new blog post |
| `GET` | `/api/v1/posts/{id}/suggestions` | Get ranked image suggestions passing Mismatch Guard |
| `POST` | `/api/v1/match/explain` | Inspect why an image was accepted or rejected |
| `POST` | `/api/v1/suggestions/{id}/approve` | Editorial workflow: Approve suggested match |
| `POST` | `/api/v1/suggestions/{id}/reject` | Editorial workflow: Reject suggestion with notes |
| `GET` | `/api/v1/analytics/costs` | Retrieve token consumption and USD cost log |
| `GET` | `/api/v1/eval/run` | Run live evaluation benchmark |

---

## 7. Limitations & Future Scope

- **Corpus Scale**: Built and tuned for a ~50 to 1,000 image catalogue. For millions of images, SQLite vector storage can be upgraded to `pgvector` or Milvus.
- **Multimodal Models**: Cloud mode relies on Gemini 1.5 Flash. If offline, the local provider uses high-dimensional semantic hash projections.
- **Taxonomy Depth**: Current taxonomic dictionary covers 7 major wildlife and domain families; expanding to open-domain ontology (e.g. Wikidata / WordNet) would scale open-vocabulary coverage.

---

## 8. License
Distributed under the MIT License. See [LICENSE](LICENSE) for details.
