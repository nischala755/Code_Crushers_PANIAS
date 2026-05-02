"""
Weighted matching engine with signal-level scoring.
Produces explainable match evidence for every candidate pair.
"""

import jellyfish
from backend.engine.normalizer import normalize_name, normalize_address, normalize_phone


# Default weights
DEFAULT_WEIGHTS = {
    "pan": 0.35,
    "gstin": 0.25,
    "name": 0.20,
    "address": 0.10,
    "phone": 0.10,
}

DEFAULT_THRESHOLDS = {
    "auto_link": 0.85,
    "review": 0.60,
}


def compute_pan_score(pan1: str, pan2: str) -> float:
    """Exact PAN match score."""
    if not pan1 or not pan2:
        return 0.0
    return 1.0 if pan1.strip().upper() == pan2.strip().upper() else 0.0


def compute_gstin_score(gstin1: str, gstin2: str) -> float:
    """GSTIN match score. Partial credit for PAN portion match."""
    if not gstin1 or not gstin2:
        return 0.0
    g1 = gstin1.strip().upper()
    g2 = gstin2.strip().upper()
    if g1 == g2:
        return 1.0
    # Check PAN portion (chars 2-12)
    if len(g1) >= 12 and len(g2) >= 12:
        if g1[2:12] == g2[2:12]:
            return 0.8
    return 0.0


def compute_name_score(name1: str, name2: str) -> float:
    """Name similarity using Jaro-Winkler distance."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 1.0
    score = jellyfish.jaro_winkler_similarity(n1, n2)
    return round(score, 4)


def compute_address_score(addr1: str, addr2: str) -> float:
    """Address similarity using token overlap (Jaccard)."""
    a1 = normalize_address(addr1)
    a2 = normalize_address(addr2)
    if not a1 or not a2:
        return 0.0
    tokens1 = set(a1.split())
    tokens2 = set(a2.split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return round(len(intersection) / len(union), 4)


def compute_phone_score(phone1: str, phone2: str) -> float:
    """Phone match score."""
    p1 = normalize_phone(phone1)
    p2 = normalize_phone(phone2)
    if not p1 or not p2:
        return 0.0
    return 1.0 if p1 == p2 else 0.0


def compute_match_score(rec1, rec2, weights=None, thresholds=None):
    """
    Compute weighted match score between two records.
    Returns a dict with individual signal scores, weighted total, and decision.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    pan_score = compute_pan_score(rec1.pan, rec2.pan)
    gstin_score = compute_gstin_score(rec1.gstin, rec2.gstin)
    name_score = compute_name_score(rec1.business_name, rec2.business_name)
    address_score = compute_address_score(rec1.address, rec2.address)
    phone_score = compute_phone_score(rec1.phone, rec2.phone)

    weighted = (
        pan_score * weights["pan"]
        + gstin_score * weights["gstin"]
        + name_score * weights["name"]
        + address_score * weights["address"]
        + phone_score * weights["phone"]
    )
    weighted = round(weighted, 4)

    if weighted >= thresholds["auto_link"]:
        decision = "AUTO_LINKED"
    elif weighted >= thresholds["review"]:
        decision = "REVIEW"
    else:
        decision = "SEPARATE"

    return {
        "pan_score": pan_score,
        "gstin_score": gstin_score,
        "name_score": name_score,
        "address_score": address_score,
        "phone_score": phone_score,
        "weighted_score": weighted,
        "decision": decision,
    }
