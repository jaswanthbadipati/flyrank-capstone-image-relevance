"""The Mismatch Guard Safety Layer.
Combines tag extraction, semantic similarity thresholds, confidence scores, and taxonomic validation
to guard against false positive pairings with human-readable diagnostic explanations.
"""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from app.config import settings
from app.models.schemas import MismatchGuardResult, GuardBreakdown

logger = logging.getLogger(__name__)

# Mutually exclusive subject taxonomy groups to prevent subtle canine/feline/ursid cross-matches
TAXONOMIC_GROUPS = {
    "canines": {
        "fennec fox": ["fennec foxes", "fennec fox", "vulpes zerda", "desert foxes", "desert fox", "desert fennec", "fennec"],
        "red fox": ["red foxes", "red fox", "vulpes vulpes", "orange fox", "vulpine", "wild fox", "foxes", "fox"],
        "gray wolf": ["gray wolves", "gray wolf", "grey wolves", "grey wolf", "canis lupus", "timber wolves", "timber wolf", "lupine", "wild wolf", "wolves", "wolf"],
        "domestic dog": ["domestic dogs", "domestic dog", "golden retrievers", "golden retriever", "canis familiaris", "puppies", "puppy", "family dog", "dogs", "dog", "retrievers", "retriever"]
    },
    "ursids": {
        "polar bear": ["polar bears", "polar bear", "ursus maritimus", "white bears", "white bear", "ice bears", "ice bear"],
        "giant panda": ["giant pandas", "giant panda", "ailuropoda melanoleuca", "pandas", "panda", "bamboo bears", "bamboo bear"],
        "grizzly bear": ["grizzly bears", "grizzly bear", "ursus arctos", "brown bears", "brown bear", "kodiak bears", "kodiak bear", "coastal grizzly"]
    },
    "felines": {
        "bengal tiger": ["bengal tigers", "bengal tiger", "panthera tigris", "tigers", "tiger"],
        "african lion": ["african lions", "african lion", "panthera leo", "lions", "lion"],
        "domestic cat": ["domestic cats", "domestic cat", "felis catus", "cats", "cat", "kittens", "kitten"]
    },
    "cervids": {
        "white-tailed deer": ["white-tailed deer", "whitetail deer", "odocoileus virginianus", "wild deer", "deer", "bucks", "buck", "does", "doe"],
        "elk": ["bull elk", "elk herd", "elk", "cervus canadensis", "wapiti", "moose"]
    },
    "raptors": {
        "bald eagle": ["bald eagles", "bald eagle", "haliaeetus leucocephalus", "american eagles", "american eagle", "eagles", "eagle"],
        "barn owl": ["barn owls", "barn owl", "tyto alba", "screech owls", "screech owl", "owls", "owl"]
    },
    "technology": {
        "server rack datacenter": [
            "cloud datacenters", "cloud datacenter", "data centers", "data center",
            "datacenters", "datacenter", "cloud infrastructure", "server racks",
            "server rack", "server architecture", "cloud computing", "enterprise servers"
        ]
    },
    "landscapes": {
        "mountain landscape": ["mountain landscape", "mountain peaks", "mountain peak", "alpine peaks", "alpine peak", "mountain range", "scenic mountains"]
    }
}

def extract_key_subject_from_text(text: str) -> Optional[Tuple[str, str]]:
    """
    Extract key biological or domain subject from post title and content.
    Returns (group_name, specific_subject_key) if identified.
    Tests longest alias phrases first to prevent sub-string collision.
    """
    text_lower = text.lower().replace("-", " ")
    
    # Collect all (group_name, canon_name, alias) tuples and sort by alias length descending
    all_patterns = []
    for group_name, subjects in TAXONOMIC_GROUPS.items():
        for canon_name, aliases in subjects.items():
            for alias in aliases:
                all_patterns.append((group_name, canon_name, alias))
                
    all_patterns.sort(key=lambda x: len(x[2]), reverse=True)
    
    for group_name, canon_name, alias in all_patterns:
        pattern = r"\b" + re.escape(alias.replace("-", " ")) + r"\b"
        if re.search(pattern, text_lower):
            return group_name, canon_name
                    
    return None

def find_candidate_canonical_subject(image_subject: str) -> Optional[Tuple[str, str]]:
    """Determine the taxonomic group and canonical name for an image subject."""
    subj_lower = image_subject.lower().replace("-", " ")
    
    all_patterns = []
    for group_name, subjects in TAXONOMIC_GROUPS.items():
        for canon_name, aliases in subjects.items():
            for alias in aliases:
                all_patterns.append((group_name, canon_name, alias))
                
    all_patterns.sort(key=lambda x: len(x[2]), reverse=True)
    
    for group_name, canon_name, alias in all_patterns:
        pattern = r"\b" + re.escape(alias.replace("-", " ")) + r"\b"
        if re.search(pattern, subj_lower):
            return group_name, canon_name
            
    return None

def evaluate_mismatch_guard(
    post_title: str,
    post_content: str,
    image_subject: str,
    image_category: str,
    image_attributes: List[str],
    image_confidence: float,
    similarity_score: float
) -> MismatchGuardResult:
    """
    Evaluates candidate image pairing against the 4-tier Mismatch Guard safety rules.
    """
    rejection_reasons: List[str] = []
    
    # 1. Vision Classification Confidence Guard
    confidence_ok = image_confidence >= settings.MIN_CONFIDENCE_THRESHOLD
    if not confidence_ok:
        rejection_reasons.append(
            f"Vision classification confidence too low: {image_confidence:.2f} (required >= {settings.MIN_CONFIDENCE_THRESHOLD:.2f})"
        )

    # 2. Semantic Similarity Threshold Guard
    similarity_ok = similarity_score >= settings.MIN_SIMILARITY_THRESHOLD
    if not similarity_ok:
        rejection_reasons.append(
            f"Semantic similarity score {similarity_score:.2f} below minimum acceptance threshold ({settings.MIN_SIMILARITY_THRESHOLD:.2f})"
        )

    # 3. Taxonomic & Subject Disambiguation Guard
    combined_post_text = f"{post_title} {post_content}".lower()
    post_taxonomy = extract_key_subject_from_text(combined_post_text)
    
    subject_match = True
    category_ok = True
    
    if post_taxonomy:
        group_name, expected_subject = post_taxonomy
        img_taxonomy = find_candidate_canonical_subject(image_subject)
        
        if img_taxonomy:
            cand_group, candidate_canon = img_taxonomy
            if cand_group == group_name and candidate_canon != expected_subject:
                subject_match = False
                rejection_reasons.append(
                    f"Subject taxonomy mismatch: post specifies '{expected_subject}', but image depicts '{candidate_canon}'"
                )
            elif cand_group != group_name:
                subject_match = False
                category_ok = False
                rejection_reasons.append(
                    f"Category mismatch: expected '{expected_subject}' ({group_name}), detected '{candidate_canon}' ({cand_group})"
                )
        else:
            # Candidate not recognized in taxonomy dictionary
            if expected_subject.lower() not in image_subject.lower():
                subject_match = False
                category_ok = False
                rejection_reasons.append(
                    f"Subject mismatch: expected '{expected_subject}', detected '{image_subject}'"
                )

    passed = len(rejection_reasons) == 0
    
    if not confidence_ok:
        status = "FLAGGED_LOW_CONFIDENCE"
    elif passed:
        status = "ACCEPTED"
    else:
        status = "REJECTED"
        
    primary_rejection_reason = " | ".join(rejection_reasons) if rejection_reasons else None
    
    breakdown = GuardBreakdown(
        confidence_ok=confidence_ok,
        similarity_ok=similarity_ok,
        category_ok=category_ok,
        subject_match=subject_match,
        confidence_score=image_confidence,
        similarity_score=similarity_score,
        rejection_reasons=rejection_reasons
    )
    
    return MismatchGuardResult(
        passed=passed,
        status=status,
        rejection_reason=primary_rejection_reason,
        confidence_score=image_confidence,
        similarity_score=similarity_score,
        breakdown=breakdown
    )
