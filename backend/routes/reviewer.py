"""
Reviewer workflow API endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import (
    MatchEvidence, DepartmentRecord, ReviewDecision, AuditEntry, UBIDLink, UBID,
)
from backend.models.schemas import (
    ReviewPairItem, ReviewPairDetail, RecordBrief, MatchEvidenceSchema,
    ReviewDecisionRequest, ReviewDecisionResponse,
)
from backend.engine.learner import apply_learning

router = APIRouter(prefix="/api/review", tags=["Reviewer"])


@router.get("/queue", response_model=list[ReviewPairItem])
def get_review_queue(db: Session = Depends(get_db)):
    """Get pending review pairs."""
    evidence_list = db.query(MatchEvidence).filter(
        MatchEvidence.decision == "REVIEW",
        MatchEvidence.reviewed == False,
    ).order_by(MatchEvidence.weighted_score.desc()).all()

    items = []
    for ev in evidence_list:
        rec1 = db.query(DepartmentRecord).filter(
            DepartmentRecord.record_id == ev.record_id_1
        ).first()
        rec2 = db.query(DepartmentRecord).filter(
            DepartmentRecord.record_id == ev.record_id_2
        ).first()

        items.append(ReviewPairItem(
            evidence_id=ev.id,
            record_id_1=ev.record_id_1,
            record_id_2=ev.record_id_2,
            name_1=rec1.business_name if rec1 else "Unknown",
            name_2=rec2.business_name if rec2 else "Unknown",
            weighted_score=ev.weighted_score,
            decision=ev.decision,
            reviewed=ev.reviewed,
        ))

    return items


@router.get("/{evidence_id}", response_model=ReviewPairDetail)
def get_review_detail(evidence_id: int, db: Session = Depends(get_db)):
    """Get detailed comparison for a review pair."""
    ev = db.query(MatchEvidence).filter(MatchEvidence.id == evidence_id).first()
    if not ev:
        return {"error": "Evidence not found"}

    rec1 = db.query(DepartmentRecord).filter(
        DepartmentRecord.record_id == ev.record_id_1
    ).first()
    rec2 = db.query(DepartmentRecord).filter(
        DepartmentRecord.record_id == ev.record_id_2
    ).first()

    return ReviewPairDetail(
        evidence=MatchEvidenceSchema.model_validate(ev),
        record_1=RecordBrief.model_validate(rec1) if rec1 else RecordBrief(record_id="?", department="?", department_display="?", business_name="?"),
        record_2=RecordBrief.model_validate(rec2) if rec2 else RecordBrief(record_id="?", department="?", department_display="?", business_name="?"),
    )


@router.post("/{evidence_id}/decide", response_model=ReviewDecisionResponse)
def submit_decision(evidence_id: int, request: ReviewDecisionRequest, db: Session = Depends(get_db)):
    """Submit a reviewer decision."""
    ev = db.query(MatchEvidence).filter(MatchEvidence.id == evidence_id).first()
    if not ev:
        return ReviewDecisionResponse(success=False, message="Evidence not found")

    # Apply learning effect
    learning_result = apply_learning(db, ev, request.decision)

    # Update evidence
    ev.reviewed = True
    ev.review_decision = request.decision
    ev.reviewed_at = datetime.utcnow()
    ev.reviewed_by = request.reviewer or "REVIEWER"

    # Store decision
    review = ReviewDecision(
        evidence_id=ev.id,
        decision=request.decision,
        reason=request.reason,
        decided_by=request.reviewer or "REVIEWER",
        confidence_before=learning_result["confidence_before"],
        confidence_after=learning_result["confidence_after"],
    )
    db.add(review)

    # If confirmed, merge the records under the same UBID
    if request.decision == "CONFIRMED":
        # Find UBIDs for both records
        link1 = db.query(UBIDLink).filter(UBIDLink.record_id == ev.record_id_1).first()
        link2 = db.query(UBIDLink).filter(UBIDLink.record_id == ev.record_id_2).first()

        if link1 and link2 and link1.ubid_id != link2.ubid_id:
            # Merge: move all records from ubid2 to ubid1
            ubid1 = db.query(UBID).filter(UBID.id == link1.ubid_id).first()
            ubid2 = db.query(UBID).filter(UBID.id == link2.ubid_id).first()

            links_to_move = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid2.id).all()
            for link in links_to_move:
                link.ubid_id = ubid1.id

            ubid1.record_count = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid1.id).count()
            depts = db.query(DepartmentRecord.department).join(
                UBIDLink, UBIDLink.record_id == DepartmentRecord.record_id
            ).filter(UBIDLink.ubid_id == ubid1.id).distinct().all()
            ubid1.department_count = len(depts)
            ubid1.confidence_score = learning_result["confidence_after"]

            # Update evidence ubid_code
            ev.ubid_code = ubid1.ubid_code

            # Delete empty UBID
            db.delete(ubid2)

    # Audit
    audit = AuditEntry(
        action=f"REVIEW_{request.decision}",
        actor=request.reviewer or "REVIEWER",
        ubid_code=ev.ubid_code,
        record_ids=f"{ev.record_id_1},{ev.record_id_2}",
        details=f"Decision: {request.decision}. Reason: {request.reason or 'N/A'}. "
                f"Confidence: {learning_result['confidence_before']:.4f} → {learning_result['confidence_after']:.4f}",
        category="REVIEW",
    )
    db.add(audit)

    db.commit()

    return ReviewDecisionResponse(
        success=True,
        message=f"Decision '{request.decision}' recorded. System learning applied.",
        confidence_before=learning_result["confidence_before"],
        confidence_after=learning_result["confidence_after"],
        weight_changes=learning_result["weight_changes"],
    )
