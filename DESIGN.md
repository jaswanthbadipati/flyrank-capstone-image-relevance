# AI Image Understanding & Content Matching Engine — Design Document

## 1. Problem Statement
Content publishing platforms require rich visual media for articles. Matching images to blog posts based purely on keywords or filenames frequently results in severe semantic mismatches—for example, pairing a wolf photo with a red-fox blog post because both share generic tags like "wild animal in forest."

This project implements an intelligent, trustworthy AI matching engine that:
1. Performs schema-validated multimodal vision analysis on an image library.
2. Embeddings captions, tags, and blog post content in a shared semantic vector space.
3. Ranks candidates via vector similarity.
4. Enforces a strict **Mismatch Guard** safety layer to catch subtle taxonomic or thematic mismatches (such as Canidae disambiguation: Fox vs. Wolf vs. Dog) and rejects pairs with low confidence or below similarity thresholds.
5. Provides human-in-the-loop review capabilities and full per-call token and cost tracking.

---

## 2. System Architecture & Layer Sketch

The system is built using a strict layered architecture:

```
+------------------------------------------------------------------------------------+
|                                 1. HTTP / Presentation Layer                       |
|   FastAPI REST Routes: /images, /posts, /suggestions, /jobs, /analytics, /eval     |
|   - Request/Response validation via Pydantic                                       |
|   - Clean 4xx/5xx HTTP error mappings                                              |
+------------------------------------------------------------------------------------+
                                           |
+------------------------------------------------------------------------------------+
|                                 2. Business Logic Layer                            |
|   +-------------------+  +--------------------+  +-------------------------------+ |
|   | Vision Service    |  | Vector Matching    |  | Mismatch Guard Safety Layer   | |
|   | - Structured JSON |  | - Dual Embeddings  |  | - Confidence check (>0.70)    | |
|   | - Schema Parser   |  | - Cosine Search    |  | - Category/Subject Matcher    | |
|   | - Low-Conf Flag   |  | - Candidate Ranker |  | - Safe Rejection Explainer    | |
|   +-------------------+  +--------------------+  +-------------------------------+ |
|   +-------------------+  +--------------------+                                    |
|   | Batch Job Worker  |  | Cost & Token Audit |                                    |
|   | - Async execution |  | - USD Attribution  |                                    |
|   | - Retry & backoff |  | - Budget guard     |                                    |
|   +-------------------+  +--------------------+                                    |
+------------------------------------------------------------------------------------+
                                           |
+------------------------------------------------------------------------------------+
|                              3. Data Access / Persistence Layer                    |
|   SQLite Engine with WAL mode, normalized tables, indexed queries, vector storage  |
+------------------------------------------------------------------------------------+
```

---

## 3. Data Model & Schema Design

### 3.1 Tables
- **`images`**:
  - `id` (TEXT PRIMARY KEY / UUID)
  - `filename` (TEXT NOT NULL)
  - `filepath` (TEXT NOT NULL)
  - `source_url` (TEXT)
  - `license` (TEXT NOT NULL)
  - `status` (TEXT: `pending`, `processed`, `flagged`, `failed`)
  - `needs_review` (BOOLEAN DEFAULT 0)
  - `flag_reason` (TEXT)
  - `created_at` (TIMESTAMP)

- **`image_metadata`**:
  - `image_id` (TEXT PRIMARY KEY REFERENCES images(id))
  - `subject` (TEXT NOT NULL)
  - `category` (TEXT NOT NULL)
  - `attributes` (TEXT JSON array)
  - `caption` (TEXT NOT NULL)
  - `confidence` (REAL NOT NULL)
  - `raw_response` (TEXT JSON)
  - `model_name` (TEXT NOT NULL)
  - `processed_at` (TIMESTAMP)

- **`embeddings`**:
  - `id` (TEXT PRIMARY KEY)
  - `entity_type` (TEXT: `image` or `post`)
  - `entity_id` (TEXT NOT NULL)
  - `embedding_json` (TEXT NOT NULL)
  - `dimension` (INTEGER NOT NULL)
  - `model_name` (TEXT NOT NULL)
  - `created_at` (TIMESTAMP)

- **`posts`**:
  - `id` (TEXT PRIMARY KEY)
  - `title` (TEXT NOT NULL)
  - `slug` (TEXT UNIQUE NOT NULL)
  - `content` (TEXT NOT NULL)
  - `target_category` (TEXT)
  - `target_subject` (TEXT)
  - `created_at` (TIMESTAMP)

- **`suggestions`**:
  - `id` (TEXT PRIMARY KEY)
  - `post_id` (TEXT REFERENCES posts(id))
  - `image_id` (TEXT REFERENCES images(id))
  - `similarity_score` (REAL NOT NULL)
  - `guard_passed` (BOOLEAN NOT NULL)
  - `rejection_reason` (TEXT)
  - `guard_breakdown` (TEXT JSON)
  - `status` (TEXT: `pending`, `approved`, `rejected`)
  - `created_at` (TIMESTAMP)

- **`cost_logs`**:
  - `id` (TEXT PRIMARY KEY)
  - `operation` (TEXT: `vision_classification`, `text_embedding`)
  - `model_name` (TEXT NOT NULL)
  - `prompt_tokens` (INTEGER NOT NULL)
  - `completion_tokens` (INTEGER NOT NULL)
  - `total_tokens` (INTEGER NOT NULL)
  - `cost_usd` (REAL NOT NULL)
  - `duration_ms` (INTEGER NOT NULL)
  - `created_at` (TIMESTAMP)

- **`jobs`**:
  - `id` (TEXT PRIMARY KEY)
  - `job_type` (TEXT: `batch_ingest`, `reindex_embeddings`)
  - `status` (TEXT: `queued`, `running`, `completed`, `failed`)
  - `total_items` (INTEGER DEFAULT 0)
  - `processed_items` (INTEGER DEFAULT 0)
  - `failed_items` (INTEGER DEFAULT 0)
  - `retry_count` (INTEGER DEFAULT 0)
  - `error_message` (TEXT)
  - `started_at` (TIMESTAMP)
  - `completed_at` (TIMESTAMP)

---

## 4. The Mismatch Guard Decision Matrix

The Mismatch Guard evaluates candidates through a 4-tier safety funnel:

1. **Classification Confidence Filter**:
   - `confidence < 0.70` $\rightarrow$ **REJECTED**: `"Vision classification confidence too low (score: {confidence:.2f} < 0.70)"`
2. **Semantic Similarity Threshold**:
   - `similarity < 0.60` $\rightarrow$ **REJECTED**: `"Semantic similarity below minimum matching threshold (score: {similarity:.2f} < 0.60)"`
3. **Category & Taxonomic Disambiguation**:
   - Check taxonomy conflicts (e.g. Post asks for Fox, candidate image is Wolf):
   - `post_subject != candidate_subject` (where post specifies exclusive subject) $\rightarrow$ **REJECTED**: `"Subject mismatch: expected '{expected}', detected '{candidate}'"`
4. **Context & Attribute Negative Filter**:
   - Conflicting habitat, environment, or key attributes (e.g. arctic polar environment for tropical feline).

If all checks pass and similarity $\ge 0.75$, the match is **CONFIDENT SUGGESTION**.
If all checks pass and $0.60 \le$ similarity $< 0.75$, the match is **SUGGESTION WITH REVIEW**.
If no image passes, the engine returns **`"no confident match"`** with comprehensive diagnostic explanations.

---

## 5. API Surface

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/jobs/ingest` | Enqueue background batch ingestion on image corpus with retries |
| `GET`  | `/api/v1/jobs/{job_id}` | Check status and progress of batch processing job |
| `GET`  | `/api/v1/images` | List ingested images and their extracted metadata |
| `GET`  | `/api/v1/images/flagged` | List images flagged for low confidence or processing issues |
| `POST` | `/api/v1/posts` | Create or import blog post |
| `GET`  | `/api/v1/posts/{post_id}/suggestions` | Retrieve ranked image suggestions passing the Mismatch Guard |
| `POST` | `/api/v1/match/explain` | Test candidate image against a post with guard breakdown |
| `POST` | `/api/v1/suggestions/{id}/approve` | Human review: Approve recommended match |
| `POST` | `/api/v1/suggestions/{id}/reject` | Human review: Reject recommended match with notes |
| `GET`  | `/api/v1/analytics/costs` | View token consumption and USD cost attribution |
| `GET`  | `/api/v1/eval/run` | Run evaluation benchmark against ground-truth dataset |

---

## 6. Explicit Non-Goals
1. Building a full frontend SPA (the project uses FastAPI Swagger UI + minimal admin table).
2. Large-scale multi-gigabyte vector databases (SQLite + in-memory cosine vector math handles 50–1,000 images with sub-millisecond latency at \$0).
3. Live payment / billing gateways (this system runs on \$0 free tier).
