"""
Learning effect simulator.
When a reviewer confirms/rejects a match, slightly adjust weights
and show confidence improvement.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.db_models import SystemWeights, MatchEvidence, AuditEntry
from backend.engine.matcher import compute_match_score


def get_weights(db: Session):
    """Get latest system weights."""
    sw = db.query(SystemWeights).order_by(SystemWeights.id.desc()).first()
    if sw:
        return {
            "pan": sw.pan_weight,
            "gstin": sw.gstin_weight,
            "name": sw.name_weight,
            "address": sw.address_weight,
            "phone": sw.phone_weight,
        }
    return {
        "pan": 0.35,
        "gstin": 0.25,
        "name": 0.20,
        "address": 0.10,
        "phone": 0.10,
    }


def apply_learning(db: Session, evidence: MatchEvidence, decision: str):
    """
    Apply learning from reviewer decision.
    - CONFIRMED: boost weights of signals that contributed to the match
    - REJECTED: reduce weights of signals that were misleading
    """
    old_weights = get_weights(db)
    new_weights = dict(old_weights)

    LEARNING_RATE = 0.02  # Small adjustment

    # Get signal scores
    signals = {
        "pan": evidence.pan_score,
        "gstin": evidence.gstin_score,
        "name": evidence.name_score,
        "address": evidence.address_score,
        "phone": evidence.phone_score,
    }

    if decision == "CONFIRMED":
        # Boost weights of strong signals (scored > 0.5)
        strong_signals = [k for k, v in signals.items() if v > 0.5]
        if strong_signals:
            boost = LEARNING_RATE / len(strong_signals)
            for sig in strong_signals:
                new_weights[sig] = min(0.50, new_weights[sig] + boost)
    elif decision == "REJECTED":
        # Reduce weights of signals that were strong but match was wrong
        strong_signals = [k for k, v in signals.items() if v > 0.5]
        if strong_signals:
            reduction = LEARNING_RATE / len(strong_signals)
            for sig in strong_signals:
                new_weights[sig] = max(0.05, new_weights[sig] - reduction)

    # Normalize weights to sum to 1
    total = sum(new_weights.values())
    if total > 0:
        new_weights = {k: round(v / total, 4) for k, v in new_weights.items()}

    # Compute before/after confidence
    confidence_before = evidence.weighted_score
    confidence_after = sum(
        signals[k] * new_weights[k] for k in signals
    )
    confidence_after = round(confidence_after, 4)

    # Save new weights
    sw = SystemWeights(
        pan_weight=new_weights["pan"],
        gstin_weight=new_weights["gstin"],
        name_weight=new_weights["name"],
        address_weight=new_weights["address"],
        phone_weight=new_weights["phone"],
        update_reason=f"Reviewer {decision} on pair {evidence.record_id_1} - {evidence.record_id_2}",
    )
    db.add(sw)

    # Audit
    audit = AuditEntry(
        action="SYSTEM_LEARNING",
        actor="SYSTEM",
        details=(
            f"Weights adjusted after reviewer {decision}. "
            f"Before: {old_weights}. After: {new_weights}. "
            f"Confidence: {confidence_before:.4f} → {confidence_after:.4f}"
        ),
        category="SYSTEM",
    )
    db.add(audit)

    return {
        "confidence_before": confidence_before,
        "confidence_after": confidence_after,
        "weight_changes": {
            "before": old_weights,
            "after": new_weights,
        },
    }
