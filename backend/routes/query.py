"""
Natural language query API endpoint.
"""

import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import (
    UBID, UBIDLink, DepartmentRecord, ActivityClassification, ActivityEvent,
)
from backend.models.schemas import QueryRequest, QueryResponse, QueryResult
from backend.services.mistral_service import interpret_query

router = APIRouter(prefix="/api/query", tags=["Query"])

REFERENCE_DATE = datetime(2025, 4, 1)


@router.post("/", response_model=QueryResponse)
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    """Interpret and execute a natural language query."""

    # Interpret query
    filters = interpret_query(request.query)
    interpreted = json.dumps(filters, indent=2)

    # Build query
    query = db.query(UBID)

    if "activity_status" in filters:
        query = query.filter(UBID.activity_status == filters["activity_status"])

    if "risk_level" in filters:
        query = query.filter(UBID.risk_level == filters["risk_level"])

    if "city" in filters:
        city = filters["city"]
        query = query.filter(UBID.primary_city.ilike(f"%{city}%"))

    if "pincode" in filters:
        query = query.filter(UBID.primary_pincode == filters["pincode"])

    if "min_confidence" in filters:
        query = query.filter(UBID.confidence_score >= float(filters["min_confidence"]))

    if "department" in filters:
        dept = filters["department"]
        subq = db.query(UBIDLink.ubid_id).join(
            DepartmentRecord, UBIDLink.record_id == DepartmentRecord.record_id
        ).filter(DepartmentRecord.department == dept).subquery()
        query = query.filter(UBID.id.in_(subq))

    ubids = query.limit(100).all()

    # Post-filter: no inspection in X months
    results = []
    no_inspection_months = filters.get("no_inspection_months")

    for ubid in ubids:
        # Get linked records
        links = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid.id).all()
        record_ids = [link.record_id for link in links]

        # Check inspection filter
        if no_inspection_months:
            inspection_types = [
                "INSPECTION_CONDUCTED", "SAFETY_INSPECTION", "BOILER_INSPECTION",
                "LABOUR_INSPECTION", "EMISSION_TEST", "EFFLUENT_SAMPLE_TEST",
            ]
            cutoff = REFERENCE_DATE - timedelta(days=no_inspection_months * 30)

            recent_inspection = db.query(ActivityEvent).filter(
                ActivityEvent.record_id.in_(record_ids),
                ActivityEvent.event_type.in_(inspection_types),
                ActivityEvent.event_date >= cutoff.strftime("%Y-%m-%d"),
            ).first()

            if recent_inspection:
                continue  # Has recent inspection, skip

        # Get departments
        records = db.query(DepartmentRecord).filter(
            DepartmentRecord.record_id.in_(record_ids)
        ).all()
        departments = list(set(r.department for r in records))

        # Get activity
        classification = db.query(ActivityClassification).filter(
            ActivityClassification.ubid_id == ubid.id
        ).first()

        reasoning = ""
        last_activity = None
        if classification:
            reasoning = classification.reasoning or ""
            last_activity = classification.last_activity_date

        results.append(QueryResult(
            ubid_code=ubid.ubid_code,
            business_name=ubid.primary_name or "",
            city=ubid.primary_city or "",
            pincode=ubid.primary_pincode or "",
            activity_status=ubid.activity_status or "UNKNOWN",
            risk_level=ubid.risk_level or "LOW",
            activity_reasoning=reasoning,
            departments=departments,
            last_activity=last_activity,
            confidence=ubid.confidence_score,
        ))

    return QueryResponse(
        query=request.query,
        interpreted_as=interpreted,
        result_count=len(results),
        results=results,
    )
