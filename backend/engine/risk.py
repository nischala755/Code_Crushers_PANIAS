"""
Risk scoring engine.
Assigns Low/Medium/High risk based on activity, inspections, and data quality.
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.db_models import (
    UBID, UBIDLink, ActivityEvent, ActivityClassification, DepartmentRecord,
)


REFERENCE_DATE = datetime(2025, 4, 1)


def compute_risk(ubid, classification, events, records):
    """
    Compute risk score for a UBID.
    Returns risk_level, risk_score, reasons, recommendation.
    """
    risk_score = 0.0
    reasons = []
    
    # Factor 1: Activity status
    if classification:
        if classification.classification == "DORMANT":
            risk_score += 30
            reasons.append("Business is dormant — no activity in 6+ months")
        elif classification.classification == "CLOSED":
            risk_score += 15
            reasons.append("Business classified as closed")

    # Factor 2: Missing inspections (>18 months)
    inspection_types = [
        "INSPECTION_CONDUCTED", "SAFETY_INSPECTION", "BOILER_INSPECTION",
        "LABOUR_INSPECTION", "EMISSION_TEST", "EFFLUENT_SAMPLE_TEST",
    ]
    last_inspection = None
    for e in events:
        if e.event_type in inspection_types:
            try:
                d = datetime.strptime(e.event_date, "%Y-%m-%d")
                if last_inspection is None or d > last_inspection:
                    last_inspection = d
            except ValueError:
                pass

    if last_inspection:
        days_since_inspection = (REFERENCE_DATE - last_inspection).days
        if days_since_inspection > 540:  # 18 months
            risk_score += 25
            reasons.append(f"No inspection in {days_since_inspection} days (>{18} months)")
        elif days_since_inspection > 365:  # 12 months
            risk_score += 15
            reasons.append(f"No inspection in {days_since_inspection} days (>12 months)")
    else:
        if classification and classification.classification != "CLOSED":
            risk_score += 20
            reasons.append("No inspection records found")

    # Factor 3: Data inconsistencies
    if len(records) > 1:
        names = set(r.business_name.lower().strip() for r in records)
        if len(names) > 1:
            risk_score += 10
            reasons.append("Inconsistent business names across departments")

        pans = set(r.pan for r in records if r.pan)
        if len(pans) > 1:
            risk_score += 15
            reasons.append("Multiple PAN numbers found across records")

    # Factor 4: Low confidence linking
    if ubid.confidence_score < 0.7 and ubid.record_count > 1:
        risk_score += 15
        reasons.append(f"Low linking confidence ({ubid.confidence_score:.0%})")

    # Factor 5: Missing compliance signals
    if classification:
        try:
            missing = json.loads(classification.signals_missing or "[]")
            if "License Renewal" in missing and classification.classification != "CLOSED":
                risk_score += 10
                reasons.append("Missing license renewal records")
            if "Contribution" in missing and classification.classification == "ACTIVE":
                risk_score += 5
                reasons.append("Missing ESI/PF contribution records")
        except json.JSONDecodeError:
            pass

    # Cap at 100
    risk_score = min(risk_score, 100)

    # Determine level
    if risk_score >= 60:
        risk_level = "HIGH"
        recommendation = "Immediate inspection recommended"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
        recommendation = "Schedule monitoring visit within 3 months"
    else:
        risk_level = "LOW"
        recommendation = "No immediate action required"

    if not reasons:
        reasons.append("No significant risk factors identified")

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "reasons": reasons,
        "recommendation": recommendation,
    }


def run_risk_scoring(db: Session):
    """Run risk scoring for all UBIDs."""
    print("[RISK] Running risk scoring...")

    ubids = db.query(UBID).all()

    for ubid in ubids:
        # Get linked records
        links = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid.id).all()
        record_ids = [link.record_id for link in links]

        records = db.query(DepartmentRecord).filter(
            DepartmentRecord.record_id.in_(record_ids)
        ).all()

        events = db.query(ActivityEvent).filter(
            ActivityEvent.record_id.in_(record_ids)
        ).all()

        classification = db.query(ActivityClassification).filter(
            ActivityClassification.ubid_id == ubid.id
        ).first()

        result = compute_risk(ubid, classification, events, records)

        ubid.risk_level = result["risk_level"]
        ubid.risk_score = result["risk_score"]

    db.commit()

    counts = {}
    for ubid in ubids:
        r = ubid.risk_level
        counts[r] = counts.get(r, 0) + 1
    print(f"[RISK] Risk scoring complete: {counts}")
