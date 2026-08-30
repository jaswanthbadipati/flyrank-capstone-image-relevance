"""Evaluation benchmark script.
Measures Top-1 Precision and Mismatch Guard rejection accuracy on the labeled evaluation dataset.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.database import get_db, init_db
from app.services.matcher import match_post_to_images, explain_candidate_pairing
from app.models.schemas import EvalRunResponse, EvalResultItem

def run_benchmark() -> EvalRunResponse:
    """Executes benchmark over eval dataset."""
    init_db()
    dataset_path = ROOT_DIR / "eval" / "dataset.json"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at {dataset_path}")
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    results = []
    positive_correct = 0
    total_positives = 0
    negative_correct = 0
    total_negatives = 0
    
    print("\n" + "=" * 90)
    print("AI Image Understanding & Content Matching Engine — Evaluation Benchmark")
    print("=" * 90)
    print(f"{'Sample ID':<30} | {'Type':<10} | {'Expected':<18} | {'Actual Subject':<18} | {'Score':<6} | {'Status'}")
    print("-" * 90)
    
    for s in samples:
        sample_id = s["id"]
        title = s["title"]
        content = s["content"]
        is_distractor = s.get("is_distractor", False)
        expected_subj = s.get("expected_subject")
        
        # Ensure post is registered in DB
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO posts (id, title, slug, content, target_category, target_subject, created_at)
                VALUES (?, ?, ?, ?, 'eval', ?, CURRENT_TIMESTAMP)
                """,
                (sample_id, title, f"slug-{sample_id}", content, expected_subj)
            )
            
        # Run matching engine
        resp = match_post_to_images(sample_id, limit=3)
        
        top1_correct = False
        guard_rejection_correct = False
        actual_subj = "None (Refused)"
        sim_score = 0.0
        
        if is_distractor:
            total_negatives += 1
            if resp.status == "no_confident_match" and resp.top_match is None:
                negative_correct += 1
                guard_rejection_correct = True
                status_str = "[PASS] Correctly Refused"
            else:
                status_str = "[FAIL] False Acceptance"
                actual_subj = resp.top_match.subject if resp.top_match else "Unknown"
        else:
            total_positives += 1
            if resp.top_match:
                actual_subj = resp.top_match.subject
                sim_score = resp.top_match.similarity_score
                # Verify subject match
                if expected_subj and expected_subj.lower() in actual_subj.lower():
                    positive_correct += 1
                    top1_correct = True
                    status_str = f"[PASS] Top-1 Match ({resp.top_match.filename})"
                else:
                    status_str = f"[FAIL] Subject Mismatch: {actual_subj}"
            else:
                status_str = f"[FAIL] Unexpected Refusal ({resp.explanation})"
                
        print(f"{sample_id:<30} | {('Distractor' if is_distractor else 'Positive'):<10} | {str(expected_subj):<18} | {actual_subj:<18} | {sim_score:<6.2f} | {status_str}")
        
        results.append(EvalResultItem(
            post_id=sample_id,
            post_title=title,
            expected_image_id=s.get("expected_image_id"),
            actual_image_id=resp.top_match.image_id if resp.top_match else None,
            actual_status=resp.status,
            top1_correct=top1_correct,
            guard_rejection_correct=guard_rejection_correct,
            similarity_score=sim_score,
            notes=resp.explanation
        ))

    # Add hardcoded Fox vs Wolf forced distractor check
    total_negatives += 1
    forced_wolf_res = explain_candidate_pairing("eval_01_red_fox", "img_gray_wolf_01")
    if not forced_wolf_res.guard_passed:
        negative_correct += 1
        forced_wolf_correct = True
    else:
        forced_wolf_correct = False
        
    print(f"{'forced_wolf_on_fox_post':<30} | {'Forced Neg':<10} | {'REJECT WOLF':<18} | {'Rejected (Wolf)':<18} | {forced_wolf_res.similarity_score:<6.2f} | {('[PASS] Refused by Guard' if forced_wolf_correct else '[FAIL]')}")

    top1_precision = round((positive_correct / total_positives) * 100.0, 2) if total_positives > 0 else 0.0
    guard_rejection_acc = round((negative_correct / total_negatives) * 100.0, 2) if total_negatives > 0 else 0.0
    false_pos_rate = round(((total_negatives - negative_correct) / total_negatives) * 100.0, 2) if total_negatives > 0 else 0.0

    print("=" * 90)
    print("EVALUATION SUMMARY RESULTS:")
    print(f"  • Total Evaluated Samples:        {len(samples) + 1}")
    print(f"  • Positive Concept Samples:       {total_positives}")
    print(f"  • Negative / Distractor Samples:  {total_negatives}")
    print(f"  • Top-1 Precision:                {top1_precision:.1f}% ({positive_correct}/{total_positives})")
    print(f"  • Guard Rejection Accuracy:       {guard_rejection_acc:.1f}% ({negative_correct}/{total_negatives})")
    print(f"  • False Positive Rate:            {false_pos_rate:.1f}%")
    print("=" * 90 + "\n")

    return EvalRunResponse(
        total_eval_samples=len(samples) + 1,
        positive_samples=total_positives,
        negative_distractor_samples=total_negatives,
        top1_precision=top1_precision,
        guard_rejection_accuracy=guard_rejection_acc,
        false_positive_rate=false_pos_rate,
        timestamp=datetime.utcnow().isoformat(),
        results=results
    )

if __name__ == "__main__":
    run_benchmark()
