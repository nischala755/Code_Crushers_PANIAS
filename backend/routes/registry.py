"""
UBID Registry API endpoints.
"""

import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.db_models import (
    UBID, UBIDLink, DepartmentRecord, MatchEvidence,
    ActivityClassification, ActivityEvent,
)
from backend.models.schemas import (
    UBIDListItem, UBIDDetail, RecordBrief, MatchEvidenceSchema,
    ActivitySchema, RiskSchema, DashboardStats,
)

router = APIRouter(prefix="/api/registry", tags=["Registry"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """Dashboard statistics."""
    total_records = db.query(DepartmentRecord).count()
    total_ubids = db.query(UBID).count()

    pending_reviews = db.query(MatchEvidence).filter(
        MatchEvidence.decision == "REVIEW",
        MatchEvidence.reviewed == False
    ).count()

    active = db.query(UBID).filter(UBID.activity_status == "ACTIVE").count()
    dormant = db.query(UBID).filter(UBID.activity_status == "DORMANT").count()
    closed = db.query(UBID).filter(UBID.activity_status == "CLOSED").count()

    high_risk = db.query(UBID).filter(UBID.risk_level == "HIGH").count()
    medium_risk = db.query(UBID).filter(UBID.risk_level == "MEDIUM").count()
    low_risk = db.query(UBID).filter(UBID.risk_level == "LOW").count()

    auto_linked = db.query(MatchEvidence).filter(MatchEvidence.decision == "AUTO_LINKED").count()
    manual_reviewed = db.query(MatchEvidence).filter(MatchEvidence.reviewed == True).count()

    # Department counts
    dept_counts = {}
    for dept in ["SHOPS_ESTABLISHMENT", "FACTORIES", "LABOUR", "POLLUTION_BOARD"]:
        cnt = db.query(DepartmentRecord).filter(DepartmentRecord.department == dept).count()
        dept_counts[dept] = cnt

    return DashboardStats(
        total_records=total_records,
        total_ubids=total_ubids,
        pending_reviews=pending_reviews,
        active_count=active,
        dormant_count=dormant,
        closed_count=closed,
        department_counts=dept_counts,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        auto_linked=auto_linked,
        manual_reviewed=manual_reviewed,
    )


@router.get("/", response_model=list[UBIDListItem])
def list_ubids(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    department: Optional[str] = None,
    activity_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    city: Optional[str] = None,
    pincode: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "ubid_code",
    sort_dir: Optional[str] = "asc",
    db: Session = Depends(get_db),
):
    """List UBIDs with filters and pagination."""
    query = db.query(UBID)

    if activity_status:
        query = query.filter(UBID.activity_status == activity_status)
    if risk_level:
        query = query.filter(UBID.risk_level == risk_level)
    if city:
        query = query.filter(UBID.primary_city.ilike(f"%{city}%"))
    if pincode:
        query = query.filter(UBID.primary_pincode == pincode)
    if search:
        query = query.filter(
            UBID.primary_name.ilike(f"%{search}%") |
            UBID.ubid_code.ilike(f"%{search}%") |
            UBID.primary_pan.ilike(f"%{search}%")
        )
    if department:
        # Filter by UBIDs that have records in this department
        subq = db.query(UBIDLink.ubid_id).join(
            DepartmentRecord, UBIDLink.record_id == DepartmentRecord.record_id
        ).filter(DepartmentRecord.department == department).subquery()
        query = query.filter(UBID.id.in_(subq))

    # Sorting
    sort_col = getattr(UBID, sort_by, UBID.ubid_code)
    if sort_dir == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    offset = (page - 1) * page_size
    ubids = query.offset(offset).limit(page_size).all()

    return [UBIDListItem.model_validate(u) for u in ubids]


@router.get("/count")
def count_ubids(
    department: Optional[str] = None,
    activity_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    city: Optional[str] = None,
    pincode: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get total count for pagination."""
    query = db.query(UBID)
    if activity_status:
        query = query.filter(UBID.activity_status == activity_status)
    if risk_level:
        query = query.filter(UBID.risk_level == risk_level)
    if city:
        query = query.filter(UBID.primary_city.ilike(f"%{city}%"))
    if pincode:
        query = query.filter(UBID.primary_pincode == pincode)
    if search:
        query = query.filter(
            UBID.primary_name.ilike(f"%{search}%") |
            UBID.ubid_code.ilike(f"%{search}%")
        )
    if department:
        subq = db.query(UBIDLink.ubid_id).join(
            DepartmentRecord, UBIDLink.record_id == DepartmentRecord.record_id
        ).filter(DepartmentRecord.department == department).subquery()
        query = query.filter(UBID.id.in_(subq))

    return {"count": query.count()}


@router.get("/{ubid_code}", response_model=UBIDDetail)
def get_ubid_detail(ubid_code: str, db: Session = Depends(get_db)):
    """Full UBID detail with linked records, evidence, activity, risk."""
    ubid = db.query(UBID).filter(UBID.ubid_code == ubid_code).first()
    if not ubid:
        return {"error": "UBID not found"}

    # Linked records
    links = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid.id).all()
    record_ids = [link.record_id for link in links]

    records = db.query(DepartmentRecord).filter(
        DepartmentRecord.record_id.in_(record_ids)
    ).all()

    linked_records = [RecordBrief.model_validate(r) for r in records]

    # Match evidence
    evidence = db.query(MatchEvidence).filter(
        MatchEvidence.ubid_code == ubid_code
    ).all()
    match_evidence = [MatchEvidenceSchema.model_validate(e) for e in evidence]

    # Activity
    classification = db.query(ActivityClassification).filter(
        ActivityClassification.ubid_id == ubid.id
    ).first()
    activity = ActivitySchema.model_validate(classification) if classification else None

    # Events
    events = db.query(ActivityEvent).filter(
        ActivityEvent.record_id.in_(record_ids)
    ).order_by(ActivityEvent.event_date.desc()).all()
    events_list = [
        {
            "event_type": e.event_type,
            "event_date": e.event_date,
            "description": e.description,
            "department": e.department,
            "status": e.status,
        }
        for e in events
    ]

    # Risk
    risk_reasons = []
    if ubid.risk_level == "HIGH":
        risk_reasons = ["High risk — immediate attention required"]
    elif ubid.risk_level == "MEDIUM":
        risk_reasons = ["Medium risk — monitoring recommended"]

    risk = RiskSchema(
        risk_level=ubid.risk_level or "LOW",
        risk_score=ubid.risk_score or 0.0,
        reasons=risk_reasons,
        recommendation="No Action" if ubid.risk_level == "LOW" else "Monitor",
    )

    return UBIDDetail(
        id=ubid.id,
        ubid_code=ubid.ubid_code,
        primary_name=ubid.primary_name,
        primary_owner=ubid.primary_owner,
        primary_address=ubid.primary_address,
        primary_city=ubid.primary_city,
        primary_pincode=ubid.primary_pincode,
        primary_pan=ubid.primary_pan,
        primary_gstin=ubid.primary_gstin,
        primary_phone=ubid.primary_phone,
        confidence_score=ubid.confidence_score,
        activity_status=ubid.activity_status,
        risk_level=ubid.risk_level or "LOW",
        risk_score=ubid.risk_score or 0.0,
        department_count=ubid.department_count,
        record_count=ubid.record_count,
        linked_records=linked_records,
        match_evidence=match_evidence,
        activity=activity,
        risk=risk,
        events=events_list,
    )
