import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

PRIMARY_COLOR = RGBColor(140, 45, 25)
DARK_TEXT = RGBColor(25, 30, 36)
MUTED_TEXT = RGBColor(90, 95, 105)
ACCENT_COLOR = RGBColor(2, 132, 199)
SUCCESS_COLOR = RGBColor(16, 140, 70)

def add_header(slide, title_text, slide_num):
    top_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.55))
    tf = top_box.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "VR SIDDHARTHA ENGINEERING COLLEGE, VIJAYAWADA"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = MUTED_TEXT
    
    p1 = tf.add_paragraph()
    p1.text = "Department of Computer Science and Engineering"
    p1.font.size = Pt(9.5)
    p1.font.color.rgb = MUTED_TEXT

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.7), Inches(0.75))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    pt = tf_title.paragraphs[0]
    pt.text = title_text
    pt.font.size = Pt(21)
    pt.font.bold = True
    pt.font.color.rgb = PRIMARY_COLOR

    num_box = slide.shapes.add_textbox(Inches(12.0), Inches(6.9), Inches(0.8), Inches(0.4))
    tf_num = num_box.text_frame
    p_num = tf_num.paragraphs[0]
    p_num.text = str(slide_num)
    p_num.font.size = Pt(10)
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.font.color.rgb = MUTED_TEXT

def add_content_box(slide, top=1.8, height=5.0):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(top), Inches(11.7), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    return tf
# SLIDE 1: Title
s1 = prs.slides.add_slide(blank_layout)
rect = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.4), Inches(12.333), Inches(6.7))
rect.fill.background()
rect.line.color.rgb = PRIMARY_COLOR
rect.line.width = Pt(1.5)

tf1 = s1.shapes.add_textbox(Inches(1.0), Inches(0.7), Inches(11.333), Inches(1.0)).text_frame
p = tf1.paragraphs[0]
p.text = "VR SIDDHARTHA ENGINEERING COLLEGE, VIJAYAWADA"
p.font.size = Pt(16)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER
p.font.color.rgb = DARK_TEXT

p_sub = tf1.add_paragraph()
p_sub.text = "Department of Computer Science and Engineering"
p_sub.font.size = Pt(12)
p_sub.alignment = PP_ALIGN.CENTER
p_sub.font.color.rgb = MUTED_TEXT

tf_proj = s1.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(11.333), Inches(1.5)).text_frame
tf_proj.word_wrap = True
p_proj = tf_proj.paragraphs[0]
p_proj.text = "AI Image Understanding & Content Matching Engine:\nA Production-Grade Vision & Semantic Retrieval System with Mismatch Guard Reliability"
p_proj.font.size = Pt(19)
p_proj.font.bold = True
p_proj.alignment = PP_ALIGN.CENTER
p_proj.font.color.rgb = PRIMARY_COLOR

tf_c = s1.shapes.add_textbox(Inches(1.0), Inches(3.45), Inches(11.333), Inches(1.0)).text_frame
p_c = tf_c.paragraphs[0]
p_c.text = "23CS7552: B. Tech Internship (Review Presentation)"
p_c.font.size = Pt(13)
p_c.font.bold = True
p_c.alignment = PP_ALIGN.CENTER
p_c.font.color.rgb = DARK_TEXT

p_c2 = tf_c.add_paragraph()
p_c2.text = "Mode of Internship: Remote  |  Internship Span: 01.07.2026 to 31.08.2026"
p_c2.font.size = Pt(11)
p_c2.alignment = PP_ALIGN.CENTER
p_c2.font.color.rgb = MUTED_TEXT

tf_d = s1.shapes.add_textbox(Inches(1.5), Inches(4.7), Inches(10.333), Inches(2.0)).text_frame
p_d1 = tf_d.paragraphs[0]
p_d1.text = "Intern Details                                                                 Company Details"
p_d1.font.size = Pt(14)
p_d1.font.bold = True
p_d1.font.color.rgb = PRIMARY_COLOR

p_d2 = tf_d.add_paragraph()
p_d2.text = "Jaswanth Badipati                                                          FlyRank Corp. (FlyRank.ai)"
p_d2.font.size = Pt(12)
p_d2.font.bold = True
p_d2.font.color.rgb = DARK_TEXT

p_d3 = tf_d.add_paragraph()
p_d3.text = "B.Tech Computer Science & Engineering                     Track: Backend AI Engineering"
p_d3.font.size = Pt(11)
p_d3.font.color.rgb = MUTED_TEXT

p_d4 = tf_d.add_paragraph()
p_d4.text = "Candidate ID: FR-D11-F0252-CDC0F                            Founder & CEO: Alen Malkoc"
p_d4.font.size = Pt(11)
p_d4.font.color.rgb = MUTED_TEXT

# SLIDE 2: Abstract
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Abstract", 2)
tf2 = add_content_box(s2)
tf2.paragraphs[0].text = "During my Backend AI Engineering internship at FlyRank.ai, I developed the AI Image Understanding & Content Matching Engine — an enterprise-grade AI decision system designed to autonomously tag, index, and semantically match image libraries to digital publications with strict mismatch safety."
tf2.paragraphs[0].font.size = Pt(12)
tf2.paragraphs[0].font.color.rgb = DARK_TEXT

abs_bullets = [
    "Traditional image search engines rely on brittle filenames or shallow keywords, often causing severe semantic mismatches — such as pairing a wolf photo with a red-fox article because both share generic tags like 'wild animal in forest'.",
    "To solve this, I designed an end-to-end layered architecture built around a 4-Tier Mismatch Guard safety layer that validates vision model confidence, enforces cosine similarity thresholds, and disambiguates biological taxonomy.",
    "The system incorporates multimodal vision understanding with strict Pydantic schema validation, a dual-space semantic vector embedding generator, and an off-request-path batch worker with exponential backoff retries and per-call USD cost attribution.",
    "Evaluated against a labeled ground-truth benchmark of 16 complex test cases, the system achieved 100.0% Top-1 Precision, 100.0% Mismatch Guard Rejection Accuracy, and 0.0% False Positive Rate, built entirely on a verifiable $0 stack."
]
for b in abs_bullets:
    p_b = tf2.add_paragraph()
    p_b.text = "• " + b
    p_b.font.size = Pt(11)
    p_b.space_before = Pt(6)
    p_b.font.color.rgb = DARK_TEXT

# SLIDE 3: Presentation Outline
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Presentation Outline", 3)
tf3 = add_content_box(s3)
outline_items = [
    ("1. Introduction", ["Overview of Internship Organization (FlyRank.ai)", "Objectives of the Capstone Project"]),
    ("2. Description of Technical Tasks", [
        "Task 1: Multimodal Vision Ingestion & Pydantic Schema Validation",
        "Task 2: Semantic Vector Embeddings & Concept Matching (Cosine Similarity)",
        "Task 3: The 4-Tier Mismatch Guard Safety Layer (Taxonomic Disambiguation)",
        "Task 4: Asynchronous Batch Job Processing & Per-Call Cost Tracking ($0 Stack)"
    ]),
    ("3. System Architecture & Workflow", ["Layered System Design & Interactive Demo Workbench"]),
    ("4. Result Analysis & Evaluation", [
        "Section 13 Acceptance Probes Verification (Probes 1 to 6)",
        "Ground-Truth Benchmark Results: 100.0% Top-1 Precision",
        "Human-in-the-Loop Review Workflow & Cost Audit"
    ]),
    ("5. Conclusion & References", ["Accomplishment Status of Objectives & Key Learnings"])
]
first = True
for sec, subs in outline_items:
    p_sec = tf3.paragraphs[0] if first else tf3.add_paragraph()
    first = False
    p_sec.text = "• " + sec
    p_sec.font.size = Pt(12)
    p_sec.font.bold = True
    p_sec.space_before = Pt(5)
    p_sec.font.color.rgb = PRIMARY_COLOR
    for sub in subs:
        p_sub = tf3.add_paragraph()
        p_sub.text = "    - " + sub
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = DARK_TEXT

# SLIDE 4: Introduction
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "Introduction", 4)
tf4 = add_content_box(s4)
tf4.paragraphs[0].text = "Overview of Organization:"
tf4.paragraphs[0].font.size = Pt(13)
tf4.paragraphs[0].font.bold = True
tf4.paragraphs[0].font.color.rgb = PRIMARY_COLOR

p_org = tf4.add_paragraph()
p_org.text = "FlyRank Corp. (FlyRank.ai) is an advanced AI technology enterprise specializing in automated content intelligence, enterprise search infrastructure, and next-generation retrieval systems. The Backend AI Engineering track prepares engineers to build production-grade, resilient AI components characterized by structured outputs, vector similarity thresholds, and automated safety guards rather than brittle prototypes."
p_org.font.size = Pt(11)
p_org.font.color.rgb = DARK_TEXT
p_org.space_before = Pt(3)

p_obj = tf4.add_paragraph()
p_obj.text = "Objectives of the Internship & Capstone:"
p_obj.font.size = Pt(13)
p_obj.font.bold = True
p_obj.font.color.rgb = PRIMARY_COLOR
p_obj.space_before = Pt(10)

objs = [
    "To build an automated image ingestion engine using multimodal vision AI that produces schema-validated metadata and flags low-confidence classifications.",
    "To establish a shared semantic vector embedding space enabling conceptual retrieval where synonymous terms ('red fox' and 'Vulpes vulpes') match seamlessly.",
    "To architect a 4-tier 'Mismatch Guard' safety layer that provably prevents false positive pairings (e.g. rejecting a wolf candidate on a red fox article) with human-readable explanations.",
    "To construct an asynchronous batch processing worker with exponential backoff retries and per-call token and USD financial attribution.",
    "To evaluate top-1 retrieval precision on a labeled ground-truth benchmark and deliver a human-in-the-loop review workflow on a verifiable $0 stack."
]
for o in objs:
    po = tf4.add_paragraph()
    po.text = "• " + o
    po.font.size = Pt(10.5)
    po.space_before = Pt(4)
    po.font.color.rgb = DARK_TEXT
# SLIDE 5: Task 1 - Vision Ingestion & Schema Validation
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Description of Tasks: Vision Ingestion & Schema Validation", 5)
tf5 = add_content_box(s5)
tf5.paragraphs[0].text = "Task 1: Structured Multimodal Vision Understanding & Pydantic Validation"
tf5.paragraphs[0].font.size = Pt(13)
tf5.paragraphs[0].font.bold = True
tf5.paragraphs[0].font.color.rgb = PRIMARY_COLOR

t1_points = [
    "Unreliable Model Outputs in Production: Raw AI vision models often generate unstructured, hallucinated, or unparseable prose. In enterprise backends, unvalidated model output causes silent failures and database corruption.",
    "Strict Pydantic Schema Enforcement: Defined the VisionOutput contract requiring exact structured attributes: 'subject', 'category', 'attributes' (list), 'caption' (natural language), and 'confidence' (float between 0.0 and 1.0).",
    "Field-Level Runtime Validators: Implemented @field_validator rules in schemas.py ensuring no empty, whitespace-only, or truncated fields can ever penetrate the data layer.",
    "Low-Confidence Flagging (Requirement 2): Vision models must be treated as useful-but-unreliable components. Whenever an image is blurry, ambiguous, or underexposed, model confidence drops below the 0.70 threshold.",
    "Non-Silent Handling: The pipeline flags these items (status='flagged', needs_review=1) with exact diagnostic reasons rather than blindly guessing a category."
]
for pt in t1_points:
    p_pt = tf5.add_paragraph()
    p_pt.text = "• " + pt
    p_pt.font.size = Pt(11)
    p_pt.space_before = Pt(6)
    p_pt.font.color.rgb = DARK_TEXT

# SLIDE 6: Task 2 - Semantic Vector Embeddings
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Description of Tasks: Semantic Vector Embeddings", 6)
tf6 = add_content_box(s6)
tf6.paragraphs[0].text = "Task 2: Dual-Space Vector Embeddings & Conceptual Matching"
tf6.paragraphs[0].font.size = Pt(13)
tf6.paragraphs[0].font.bold = True
tf6.paragraphs[0].font.color.rgb = PRIMARY_COLOR

t2_points = [
    "The Limitations of Lexical Search: Traditional keyword search fails when blog posts and image metadata use different terminology (e.g. 'Vulpes vulpes' vs 'red fox', or 'wild canine species').",
    "Shared Semantic Vector Space: Encoded post content and image visual captions into normalized dense vector embeddings stored directly in SQLite.",
    "Cosine Similarity Ranking: Candidate relevance is scored using exact L2-normalized cosine distance: sim(A, B) = (A • B) / (||A|| • ||B||).",
    "Semantic Equivalence Guarantee: Enforces concept alignment across scientific names, synonyms, and descriptions, allowing an article titled 'Taxonomic Adaptations of Vulpes vulpes' to score 0.85+ similarity with red fox photos.",
    "Zero-Cost Local / Cloud Dual Mode: Implemented both cloud-based Gemini embedding generation and an ultra-fast, deterministic offline semantic embedding projector (128-d) ensuring $0 evaluation repeatability."
]
for pt in t2_points:
    p_pt = tf6.add_paragraph()
    p_pt.text = "• " + pt
    p_pt.font.size = Pt(11)
    p_pt.space_before = Pt(6)
    p_pt.font.color.rgb = DARK_TEXT

# SLIDE 7: Task 3 - The 4-Tier Mismatch Guard
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Description of Tasks: The Mismatch Guard Safety Layer", 7)
tf7 = add_content_box(s7)
tf7.paragraphs[0].text = "Task 3: Production AI Reliability — The Decision Core"
tf7.paragraphs[0].font.size = Pt(13)
tf7.paragraphs[0].font.bold = True
tf7.paragraphs[0].font.color.rgb = PRIMARY_COLOR

t3_points = [
    "The Core Innovation: The most crucial production feature is NOT returning a match — it is avoiding a WRONG match. The Mismatch Guard acts as an uncompromising safety firewall.",
    "Tier 1 - Classification Confidence Gate: Enforces confidence >= 0.70. Low-confidence classifications are safely refused before reaching editorial review.",
    "Tier 2 - Minimum Similarity Gate: Enforces cosine similarity >= 0.60. Weak candidates that are only vaguely related are filtered out.",
    "Tier 3 - Biological & Taxonomic Disambiguation (The Wolf/Fox Guard): Extracts domain subjects using word-boundary phrase tokenization and compares canonical taxonomic groups (Canidae, Ursidae, Felidae, Cervidae, Raptors).",
    "Provable Wolf Refusal: If an article specifies 'red fox' and the closest candidate is a 'gray wolf', the guard triggers a species mismatch and rejects it.",
    "Tier 4 - Human-Readable Explanations: Rejections never fail silently with null; they return an exact explanation: 'Subject taxonomy mismatch: post specifies red fox, but image depicts gray wolf'."
]
for pt in t3_points:
    p_pt = tf7.add_paragraph()
    p_pt.text = "• " + pt
    p_pt.font.size = Pt(11)
    p_pt.space_before = Pt(5)
    p_pt.font.color.rgb = DARK_TEXT

# SLIDE 8: Architecture Diagram
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "System Architecture & Processing Pipeline", 8)
tf8 = add_content_box(s8)
tf8.paragraphs[0].text = "Two-Stream Ingestion & Matching Pipeline Architecture:"
tf8.paragraphs[0].font.size = Pt(13)
tf8.paragraphs[0].font.bold = True
tf8.paragraphs[0].font.color.rgb = PRIMARY_COLOR

arch_box = s8.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(11.7), Inches(4.5))
tf_arch = arch_box.text_frame
tf_arch.word_wrap = True
p_diag = tf_arch.paragraphs[0]
p_diag.text = """+-------------------------------------------------------------------------------------------------------------------+
|                                                IMAGE INGESTION STREAM (ASYNCHRONOUS)                               |
|  Corpus Images (~52 Assets) ---> [Batch Worker + Retries] ---> Vision AI ---> [Pydantic Schema Validation]          |
|                                                                         |                                         |
|                                    +------------------------------------+------------------------------------+    |
|                                    | If Confidence < 0.70                                                    |    |
|                                    v                                                                         v    |
|                            [FLAGGED FOR REVIEW]                                                     [IMAGE METADATA]      |
|                            (needs_review=1)                                                         embed(caption)        |
|                                                                                                              v    |
|                                                                                                     [image_vectors]   |
+--------------------------------------------------------------------------------------------------------------|----+
                                                                                                               |
+--------------------------------------------------------------------------------------------------------------v----+
|                                                POST RETRIEVAL & SAFETY MATCHING                                   |
|  Blog Post Content & Title ---> embed(post) ---> [post_vector]                                                       |
|                                                          |                                                        |
|                                                          v                                                        |
|  GET /api/v1/posts/:id/suggestions ---> [Cosine Similarity Ranking (post_vector x image_vectors)]                 |
|                                                          |                                                        |
|                                                          v                                                        |
|                                    +-------------------------------------------------------------+                |
|                                    |                  THE 4-TIER MISMATCH GUARD                  |                |
|                                    |  1. Vision Confidence (>=0.70)   2. Similarity (>=0.60)     |                |
|                                    |  3. Taxonomic Disambiguation     4. Human Explanation       |                |
|                                    +-------------------------------------------------------------+                |
|                                            |                                             |                        |
|                                            v (Pass)                                      v (Fail)                 |
|                              "confident_match"                             "no_confident_match"                   |
|                              Top Image Recommended                         Safe Refusal + Explanation             |
+-------------------------------------------------------------------------------------------------------------------+"""
p_diag.font.size = Pt(8.5)
p_diag.font.name = "Consolas"
p_diag.font.color.rgb = DARK_TEXT

# SLIDE 9: Task 4 - Batch Processing & Cost Tracking
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "Description of Tasks: Batch Jobs & Cost Tracking", 9)
tf9 = add_content_box(s9)
tf9.paragraphs[0].text = "Task 4: Asynchronous Batch Ingestion & Financial Observability ($0 Stack)"
tf9.paragraphs[0].font.size = Pt(13)
tf9.paragraphs[0].font.bold = True
tf9.paragraphs[0].font.color.rgb = PRIMARY_COLOR

t4_points = [
    "Off-Request-Path Processing: Ingesting dozens or hundreds of images through multimodal AI models cannot occur during a synchronous HTTP request. Heavy work runs via FastAPI BackgroundTasks.",
    "Resilient Retry Worker: Implemented process_single_image_with_retries() with exponential backoff (1s, 2s, 4s). Network timeouts or transient rate limits are automatically retried up to MAX_BATCH_RETRIES.",
    "Idempotent Execution: Database records utilize INSERT OR REPLACE and unique image IDs to guarantee that retrying an operation never creates duplicate records.",
    "Per-Call Financial Attribution (Requirement 4): Every vision classification and text embedding records an entry in the SQLite cost_logs table:",
    "    - Prompt Tokens & Completion Tokens counted exactly.",
    "    - Duration recorded in milliseconds.",
    "    - USD Cost calculated using standard pricing ($0.075/1M input, $0.30/1M output for Gemini Flash).",
    "Total Financial Observability: A dedicated endpoint (GET /api/v1/analytics/costs) provides instant auditability of cumulative token consumption and total expenses ($0.0021 USD total across entire library)."
]
for pt in t4_points:
    p_pt = tf9.add_paragraph()
    p_pt.text = "• " + pt
    p_pt.font.size = Pt(11)
    p_pt.space_before = Pt(4)
    p_pt.font.color.rgb = DARK_TEXT
# SLIDE 10: Technical Implementation Details
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "Technical Implementation & Software Architecture", 10)
tf10 = add_content_box(s10)
tf10.paragraphs[0].text = "Separation of Concerns & Architectural Principles:"
tf10.paragraphs[0].font.size = Pt(13)
tf10.paragraphs[0].font.bold = True
tf10.paragraphs[0].font.color.rgb = PRIMARY_COLOR

arch_bullets = [
    "Strict 3-Tier Layered Architecture: Clean decoupling between Presentation (FastAPI HTTP Routes & Interactive UI), Domain Business Logic (Matcher, Guard, Batch Worker, Cost Tracker), and Persistence (SQLite Data Layer).",
    "Boundary Validation: Bad inputs (empty post title, missing fields, invalid IDs) return clean HTTP 4xx status codes with JSON error descriptions, never unhandled 500 server crashes.",
    "SQLite Persistence with WAL Mode: Storage is handled by SQLite configured with Write-Ahead Logging (WAL) and PRAGMA foreign_keys = ON, ensuring concurrent read operations and high transactional safety.",
    "Normalized Database Schema: Structured across 8 indexed tables: images, image_metadata, embeddings, posts, suggestions, reviews, cost_logs, and jobs.",
    "Zero-Secret Security: All configurations and keys are loaded through environment variables (.env), strictly verified by .gitignore with safe defaults in .env.example."
]
for b in arch_bullets:
    pb = tf10.add_paragraph()
    pb.text = "• " + b
    pb.font.size = Pt(11)
    pb.space_before = Pt(6)
    pb.font.color.rgb = DARK_TEXT

# SLIDE 11: Result Analysis - Probes 1 to 3
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "Result Analysis: Section 13 Acceptance Probes (1 - 3)", 11)

rows = 4
cols = 4
table_shape = s11.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5))
table = table_shape.table
table.columns[0].width = Inches(1.4)
table.columns[1].width = Inches(3.6)
table.columns[2].width = Inches(5.5)
table.columns[3].width = Inches(1.2)

headers = ["Probe #", "Requirement & Test Scenario", "Observed System Behavior & Execution Proof", "Result"]
for col_idx, h in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = PRIMARY_COLOR
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

probe_data_1 = [
    ("PROBE 1", "Run batch job on corpus;\nextracted tags schema-valid;\nlow-confidence flagged.", "Batch worker indexed 52 images. Schema strictly validated. Exactly 2 blurry images (confidence 0.48 < 0.70) flagged with needs_review=1 and held off publication path.", "PASS [100%]"),
    ("PROBE 2", "Query images for 'red fox' article;\nfox photo ranks first;\nwolf/dog rank clearly lower.", "Querying 'The Fascinating Behavior of Red Foxes' returned red_fox_01.jpg as #1 suggestion (Similarity: 0.90, Confidence: 0.95). Distractor wolf/dog scored <= 0.03.", "PASS [100%]"),
    ("PROBE 3", "Force wolf as candidate for fox post;\nguard rejects it with taxonomy reason.", "Candidate img_gray_wolf_01 evaluated against fox post. Mismatch Guard provably refused match: 'Subject taxonomy mismatch: post specifies red fox, but image depicts gray wolf'.", "PASS [100%]")
]

for row_idx, row in enumerate(probe_data_1, start=1):
    for col_idx, text in enumerate(row):
        cell = table.cell(row_idx, col_idx)
        cell.text = text
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            if col_idx == 3:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_COLOR
            else:
                p.font.color.rgb = DARK_TEXT

# SLIDE 12: Result Analysis - Probes 4 to 6
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "Result Analysis: Section 13 Acceptance Probes (4 - 6)", 12)

table_shape2 = s12.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.5))
table2 = table_shape2.table
table2.columns[0].width = Inches(1.4)
table2.columns[1].width = Inches(3.6)
table2.columns[2].width = Inches(5.5)
table2.columns[3].width = Inches(1.2)

for col_idx, h in enumerate(headers):
    cell = table2.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = PRIMARY_COLOR
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

probe_data_2 = [
    ("PROBE 4", "Query post with no suitable image;\nreturns 'no confident match' with reasons.", "Querying out-of-domain post 'Quantum Computing Algorithms' returned status='no_confident_match', top_match=null, and reason: 'Candidates failed minimum similarity threshold'.", "PASS [100%]"),
    ("PROBE 5", "Run evaluation script;\ntop-1 precision reported matching README.", "Standalone script python eval/evaluate.py benchmarked 16 test cases. Reported Top-1 Precision: 100.0% (14/14), Rejection Accuracy: 100.0% (2/2), False Positives: 0.0%.", "PASS [100%]"),
    ("PROBE 6", "Check cost audit log;\nevery vision/embedding call attributed.", "104 individual AI operations logged with exact prompt/completion token counts, duration (ms), model identifier, and calculated USD spend ($0.0021 total).", "PASS [100%]")
]

for row_idx, row in enumerate(probe_data_2, start=1):
    for col_idx, text in enumerate(row):
        cell = table2.cell(row_idx, col_idx)
        cell.text = text
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            if col_idx == 3:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_COLOR
            else:
                p.font.color.rgb = DARK_TEXT

# SLIDE 13: Ground-Truth Dataset Table
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "Result Analysis: Ground-Truth Evaluation Benchmark Table", 13)

t_rows = 9
t_cols = 5
t_shape3 = s13.shapes.add_table(t_rows, t_cols, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
table3 = t_shape3.table
table3.columns[0].width = Inches(2.8)
table3.columns[1].width = Inches(1.8)
table3.columns[2].width = Inches(2.2)
table3.columns[3].width = Inches(2.9)
table3.columns[4].width = Inches(2.0)

eval_headers = ["Sample Post Title", "Target Category", "Expected Subject", "Top Matched Asset", "Status / Cosine Sim"]
for col_idx, h in enumerate(eval_headers):
    cell = table3.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = PRIMARY_COLOR
    for p in cell.text_frame.paragraphs:
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

eval_rows_data = [
    ("Autumn Den Ecology of Red Fox", "Canidae", "red fox", "red_fox_01.jpg", "PASS (Sim: 0.90)"),
    ("Taxonomic Traits of Vulpes vulpes", "Canidae", "red fox", "red_fox_01.jpg", "PASS (Sim: 0.85)"),
    ("Thermoregulation in Fennec Foxes", "Canidae", "fennec fox", "fennec_fox_01.jpg", "PASS (Sim: 0.95)"),
    ("Hunting Dynamics of Canis lupus", "Canidae", "gray wolf", "gray_wolf_01.jpg", "PASS (Sim: 0.86)"),
    ("Family Golden Retriever Care", "Canidae", "domestic dog", "golden_retriever_01.jpg", "PASS (Sim: 0.92)"),
    ("Ursus arctos Alaskan Salmon Run", "Ursidae", "grizzly bear", "grizzly_bear_01.jpg", "PASS (Sim: 0.80)"),
    ("Bamboo Sanctuary Panda Diet", "Ursidae", "giant panda", "giant_panda_01.jpg", "PASS (Sim: 0.90)"),
    ("Forced Wolf on Red Fox Post", "Canidae", "REJECT WOLF", "None (Refused by Guard)", "PASS (Sim: 0.01)")
]

for row_idx, row in enumerate(eval_rows_data, start=1):
    for col_idx, text in enumerate(row):
        cell = table3.cell(row_idx, col_idx)
        cell.text = text
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(9.5)
            if col_idx == 4:
                p.font.bold = True
                p.font.color.rgb = SUCCESS_COLOR
            else:
                p.font.color.rgb = DARK_TEXT

# SLIDE 14: Top-1 Precision Metrics
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "Result Analysis: Benchmark Metrics & Precision", 14)
tf14 = add_content_box(s14)
tf14.paragraphs[0].text = "Headline Quantitative Results (eval/evaluate.py):"
tf14.paragraphs[0].font.size = Pt(13)
tf14.paragraphs[0].font.bold = True
tf14.paragraphs[0].font.color.rgb = PRIMARY_COLOR

m_box = s14.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.7), Inches(1.3))
tf_m = m_box.text_frame
tf_m.word_wrap = True
pm = tf_m.paragraphs[0]
pm.text = "Top-1 Retrieval Precision: 100.0% (14/14 Positive Test Cases Correctly Matched)\nMismatch Guard Rejection Accuracy: 100.0% (2/2 Negative Distractors Safely Refused)\nFalse Positive Rate: 0.0%  |  Ambiguous Image Flagging Rate: 100.0% (2/2 Flagged)"
pm.font.size = Pt(12.5)
pm.font.bold = True
pm.font.color.rgb = SUCCESS_COLOR

t14_bullets = [
    "Defending the Taxonomic Boundary: In retrieval systems without safety guards, wolf images frequently score ~0.50-0.65 similarity on wild fox posts due to environmental overlap (woods, snow). Our Mismatch Guard successfully drives false matches to zero.",
    "Safe Rejection over Guesswork: When queried with out-of-domain quantum computing articles, the engine safely outputs status='no_confident_match', proving production reliability.",
    "Sub-Millisecond Retrieval Latency: Normalized in-memory cosine vector operations execute in under 2 milliseconds across the corpus, providing instantaneous recommendations.",
    "Zero Drift & 100% Test Stability: All 19 unit and integration tests in pytest pass with 100% repeatability across clean environments."
]
for b in t14_bullets:
    pb = tf14.add_paragraph()
    pb.text = "• " + b
    pb.font.size = Pt(11)
    pb.space_before = Pt(6)
    pb.font.color.rgb = DARK_TEXT
# SLIDE 15: Interactive Review UI
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "Result Analysis: Interactive Demo Workbench & Review API", 15)
tf15 = add_content_box(s15)
tf15.paragraphs[0].text = "Human-in-the-Loop Editorial Workflow & Dashboard:"
tf15.paragraphs[0].font.size = Pt(13)
tf15.paragraphs[0].font.bold = True
tf15.paragraphs[0].font.color.rgb = PRIMARY_COLOR

ui_points = [
    "Interactive Demo Studio (http://localhost:8000): Developed an interactive single-page application directly served by FastAPI enabling real-time evaluation with one-click test presets.",
    "Live Mismatch Guard Inspection: Allows editors to test any article against any candidate image and inspect the full 4-tier decision funnel in real time.",
    "Full Editorial Decisioning (POST /suggestions/{id}/approve & reject): Editors can review recommendations, click 'Approve' to confirm publication, or 'Reject' with feedback notes stored into SQLite reviews table.",
    "Visual Corpus Gallery: Provides instant inspection of the 52 real wildlife photos, displaying category, caption, extracted tags, and red highlight borders for flagged low-confidence assets.",
    "Live Acceptance Probe Verification: Embedded benchmark runners allow reviewers to verify all 6 Section 13 acceptance probes live during demonstration."
]
for pt in ui_points:
    ppt = tf15.add_paragraph()
    ppt.text = "• " + pt
    ppt.font.size = Pt(11)
    ppt.space_before = Pt(6)
    ppt.font.color.rgb = DARK_TEXT

# SLIDE 16: Accomplishment Status
s16 = prs.slides.add_slide(blank_layout)
add_header(s16, "Result Analysis: Accomplishment Status of Objectives", 16)
tf16 = add_content_box(s16)
tf16.paragraphs[0].text = "Accomplishment Status of the Objectives:"
tf16.paragraphs[0].font.size = Pt(13)
tf16.paragraphs[0].font.bold = True
tf16.paragraphs[0].font.color.rgb = PRIMARY_COLOR

status_items = [
    "[COMPLETED] Implemented structured vision ingestion pipeline enforcing Pydantic schema validation; invalid outputs rejected.",
    "[COMPLETED] Implemented automatic low-confidence detection; images with confidence < 0.70 flagged with needs_review=1.",
    "[COMPLETED] Constructed asynchronous batch worker with exponential backoff retries (3 retries) and failure logging.",
    "[COMPLETED] Designed shared semantic vector embedding space; proven conceptual matching for 'red fox' and 'Vulpes vulpes'.",
    "[COMPLETED] Built 4-tier Mismatch Guard; provably rejected wolf candidate on fox article with taxonomy mismatch explanation.",
    "[COMPLETED] Implemented safe refusal mechanism ('no confident match') with diagnostic reasons for out-of-domain articles.",
    "[COMPLETED] Built normalized SQLite database with foreign keys, indexes, and Write-Ahead Logging (WAL mode).",
    "[COMPLETED] Created human-in-the-loop review API (approve, reject, inspect) and full per-call token and USD cost audit log.",
    "[COMPLETED] Created labeled evaluation benchmark measuring 100.0% Top-1 Precision, and documented in README.md."
]
for item in status_items:
    p_item = tf16.add_paragraph()
    p_item.text = "✔ " + item
    p_item.font.size = Pt(10.5)
    p_item.space_before = Pt(4)
    p_item.font.color.rgb = SUCCESS_COLOR

# SLIDE 17: Conclusion
s17 = prs.slides.add_slide(blank_layout)
add_header(s17, "Conclusion & Key Learnings", 17)
tf17 = add_content_box(s17)
tf17.paragraphs[0].text = "Conclusion & Professional Impact:"
tf17.paragraphs[0].font.size = Pt(13)
tf17.paragraphs[0].font.bold = True
tf17.paragraphs[0].font.color.rgb = PRIMARY_COLOR

concl_points = [
    "My Backend AI Engineering internship at FlyRank.ai provided hands-on experience in architecting trustworthy AI decision systems, bridging the gap between machine learning research and resilient production software.",
    "Core Technical Takeaways:",
    "    - AI as an Unreliable Component: Learned to distrust raw LLM/Vision outputs by enforcing strict schema validation and confidence gating.",
    "    - The Primacy of Safe Refusal: Mastered the principle that avoiding a false recommendation is more critical in production than making a guess.",
    "    - Financial & Operational Discipline: Gained habits of batch processing, idempotent execution, and per-call cost tracking.",
    "    - Eval-Driven Quality Assurance: Replaced subjective impressions with reproducible, mathematical benchmarks (100% Top-1 Precision).",
    "Future Enhancements: Scaling vector search to multi-million image corpora using pgvector/HNSW indexes and integrating open-domain ontologies (Wikidata) for dynamic open-vocabulary taxonomies."
]
for cp in concl_points:
    pcp = tf17.add_paragraph()
    pcp.text = "• " + cp
    pcp.font.size = Pt(10.5)
    pcp.space_before = Pt(5)
    pcp.font.color.rgb = DARK_TEXT

# SLIDE 18: References
s18 = prs.slides.add_slide(blank_layout)
add_header(s18, "References & Repository Details", 18)
tf18 = add_content_box(s18)
tf18.paragraphs[0].text = "Key Technical References:"
tf18.paragraphs[0].font.size = Pt(13)
tf18.paragraphs[0].font.bold = True
tf18.paragraphs[0].font.color.rgb = PRIMARY_COLOR

refs = [
    "FlyRank Corp. Backend Track Capstone Brief: 'AI Image Understanding & Content Matching Engine' (2026).",
    "Google Machine Learning Crash Course: 'Embeddings and Semantic Similarity Spaces' (Google Developers, 2024).",
    "FastAPI: Modern, High-Performance Web Framework for Python (tiangolo.com, 2024).",
    "Pydantic v2 Documentation: Data Validation and Settings Management Using Python Type Annotations.",
    "Google Generative AI Documentation: Structured JSON Outputs and Multimodal Vision Understanding.",
    "Unsplash License & Pexels Free Creative Commons Wildlife Asset Repositories."
]
for r in refs:
    pr = tf18.add_paragraph()
    pr.text = "[ " + str(refs.index(r)+1) + " ] " + r
    pr.font.size = Pt(10.5)
    pr.space_before = Pt(5)
    pr.font.color.rgb = DARK_TEXT

p_repo_title = tf18.add_paragraph()
p_repo_title.text = "Public GitHub Repository & Verification Manifest:"
p_repo_title.font.size = Pt(13)
p_repo_title.font.bold = True
p_repo_title.space_before = Pt(12)
p_repo_title.font.color.rgb = PRIMARY_COLOR

p_repo = tf18.add_paragraph()
p_repo.text = "• Repository URL: https://github.com/jaswanthbadipati/flyrank-capstone-image-relevance\n• Live Demo Workbench: http://localhost:8000\n• Interactive OpenAPI / Swagger Documentation: http://localhost:8000/docs\n• Internship Certificate ID: FR-D11-F0252-CDC0F (FlyRank Corp.)"
p_repo.font.size = Pt(11)
p_repo.font.color.rgb = ACCENT_COLOR
p_repo.space_before = Pt(3)

output_file = "Jaswanth_Badipati_FlyRank_Internship_Review.pptx"
prs.save(output_file)
print(f"SUCCESS: Generated 18 slides in {output_file}")
