"""
Activity inference engine.
Classifies businesses as Active, Dormant, or Closed based on event history.
"""

import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.db_models import (
    UBID, UBIDLink, ActivityEvent, ActivityClassification, AuditEntry,
)


REFERENCE_DATE = datetime(2025, 4, 1)

ACTIVE_THRESHOLD_DAYS = 180      # 6 months
DORMANT_THRESHOLD_DAYS = 730     # 24 months


def classify_activity(events, reference_date=None):
    """
    Classify activity based on events list.
    Returns classification dict.
    """
    if reference_date is None:
        reference_date = REFERENCE_DATE

    if not events:
        return {
            "classification": "CLOSED",
            "last_activity_date": None,
            "days_since_activity": 9999,
            "reasoning": "No activity events found in any department records.",
            "signals_present": [],
            "signals_missing": ["License Renewal", "Inspection", "Filing", "Contribution"],
        }

    # Parse dates
    dated_events = []
    for e in events:
        try:
            d = datetime.strptime(e.event_date, "%Y-%m-%d")
            dated_events.append((d, e))
        except (ValueError, AttributeError):
            continue

    if not dated_events:
        return {
            "classification": "CLOSED",
            "last_activity_date": None,
            "days_since_activity": 9999,
            "reasoning": "No valid dated events found.",
            "signals_present": [],
            "signals_missing": ["License Renewal", "Inspection", "Filing"],
        }

    dated_events.sort(key=lambda x: x[0], reverse=True)
    last_date, last_event = dated_events[0]
    days_since = (reference_date - last_date).days

    # Determine signals present
    event_types = set(e.event_type for _, e in dated_events)
    signals_present = []
    signals_missing = []

    signal_map = {
        "License Renewal": ["LICENSE_RENEWAL", "FACTORY_LICENSE_RENEWAL", "CONSENT_TO_OPERATE_RENEWAL"],
        "Inspection": ["INSPECTION_CONDUCTED", "SAFETY_INSPECTION", "BOILER_INSPECTION", "LABOUR_INSPECTION"],
        "Filing/Return": ["ANNUAL_RETURN_FILED", "WAGE_RETURN_FILED", "HAZARDOUS_WASTE_REPORT"],
        "Contribution": ["ESI_CONTRIBUTION", "PF_CONTRIBUTION"],
        "Testing/Monitoring": ["EMISSION_TEST", "EFFLUENT_SAMPLE_TEST", "STACK_MONITORING"],
    }

    for signal_name, etypes in signal_map.items():
        if any(et in event_types for et in etypes):
            signals_present.append(signal_name)
        else:
            signals_missing.append(signal_name)

    # Check for closure event
    has_closure = any(e.event_type == "CLOSURE_REPORTED" for _, e in dated_events)

    # Classify
    if has_closure:
        classification = "CLOSED"
        reasoning = (
            f"Business closure reported on {last_date.strftime('%d-%b-%Y')}. "
            f"License surrendered or establishment closed."
        )
    elif days_since <= ACTIVE_THRESHOLD_DAYS:
        classification = "ACTIVE"
        reasoning = (
            f"Last activity recorded {days_since} days ago on {last_date.strftime('%d-%b-%Y')} "
            f"({last_event.event_type.replace('_', ' ').title()}). "
            f"Total {len(dated_events)} events in record. "
            f"Active signals: {', '.join(signals_present) if signals_present else 'None'}."
        )
    elif days_since <= DORMANT_THRESHOLD_DAYS:
        classification = "DORMANT"
        reasoning = (
            f"No activity for {days_since} days. Last event on {last_date.strftime('%d-%b-%Y')} "
            f"({last_event.event_type.replace('_', ' ').title()}). "
            f"Missing signals: {', '.join(signals_missing) if signals_missing else 'None'}. "
            f"Business may be inactive or unregistered from monitoring."
        )
    else:
        classification = "CLOSED"
        reasoning = (
            f"No activity for {days_since} days (>{DORMANT_THRESHOLD_DAYS // 365} years). "
            f"Last event: {last_date.strftime('%d-%b-%Y')}. "
            f"Presumed closed due to prolonged inactivity."
        )

    return {
        "classification": classification,
        "last_activity_date": last_date.strftime("%Y-%m-%d"),
        "days_since_activity": days_since,
        "reasoning": reasoning,
        "signals_present": signals_present,
        "signals_missing": signals_missing,
    }


def run_activity_inference(db: Session):
    """Run activity classification for all UBIDs."""
    print("[ACTIVITY] Running activity inference...")

    ubids = db.query(UBID).all()

    # Clear existing classifications
    db.query(ActivityClassification).delete()

    for ubid in ubids:
        # Get all linked records
        links = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid.id).all()
        record_ids = [link.record_id for link in links]

        # Get all events for these records
        events = db.query(ActivityEvent).filter(
            ActivityEvent.record_id.in_(record_ids)
        ).all()

        result = classify_activity(events)

        classification = ActivityClassification(
            ubid_id=ubid.id,
            classification=result["classification"],
            last_activity_date=result["last_activity_date"],
            days_since_activity=result["days_since_activity"],
            reasoning=result["reasoning"],
            signals_present=json.dumps(result["signals_present"]),
            signals_missing=json.dumps(result["signals_missing"]),
        )
        db.add(classification)

        # Update UBID status
        ubid.activity_status = result["classification"]

    db.commit()

    counts = {}
    for ubid in ubids:
        s = ubid.activity_status
        counts[s] = counts.get(s, 0) + 1
    print(f"[ACTIVITY] Classification complete: {counts}")
