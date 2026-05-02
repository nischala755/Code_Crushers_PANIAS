"""
Activity event history generator for businesses.
Creates realistic patterns: active, dormant, closed.
"""

import random
from datetime import datetime, timedelta


EVENT_TYPES = {
    "SHOPS_ESTABLISHMENT": [
        "LICENSE_RENEWAL",
        "ANNUAL_RETURN_FILED",
        "INSPECTION_CONDUCTED",
        "AMENDMENT_FILED",
        "COMPLAINT_REGISTERED",
    ],
    "FACTORIES": [
        "FACTORY_LICENSE_RENEWAL",
        "SAFETY_INSPECTION",
        "BOILER_INSPECTION",
        "ANNUAL_RETURN_FILED",
        "ACCIDENT_REPORTED",
        "PLAN_APPROVAL",
    ],
    "LABOUR": [
        "ESI_CONTRIBUTION",
        "PF_CONTRIBUTION",
        "WAGE_RETURN_FILED",
        "LABOUR_INSPECTION",
        "CONTRACT_REGISTRATION",
        "GRATUITY_CLAIM",
    ],
    "POLLUTION_BOARD": [
        "CONSENT_TO_OPERATE_RENEWAL",
        "EMISSION_TEST",
        "EFFLUENT_SAMPLE_TEST",
        "ENVIRONMENTAL_CLEARANCE",
        "HAZARDOUS_WASTE_REPORT",
        "STACK_MONITORING",
    ],
}

EVENT_DESCRIPTIONS = {
    "LICENSE_RENEWAL": "Shop & Establishment license renewed",
    "ANNUAL_RETURN_FILED": "Annual return filed for the financial year",
    "INSPECTION_CONDUCTED": "Routine inspection conducted by department officer",
    "AMENDMENT_FILED": "Amendment to establishment details filed",
    "COMPLAINT_REGISTERED": "Consumer/employee complaint registered",
    "FACTORY_LICENSE_RENEWAL": "Factory license renewed under Factories Act",
    "SAFETY_INSPECTION": "Safety inspection under Factories Act 1948",
    "BOILER_INSPECTION": "Boiler inspection conducted as per Indian Boilers Act",
    "ACCIDENT_REPORTED": "Workplace accident reported",
    "PLAN_APPROVAL": "Factory layout plan approved",
    "ESI_CONTRIBUTION": "ESI monthly contribution deposited",
    "PF_CONTRIBUTION": "PF monthly contribution deposited",
    "WAGE_RETURN_FILED": "Quarterly wage return filed",
    "LABOUR_INSPECTION": "Labour inspection conducted",
    "CONTRACT_REGISTRATION": "Contract labour registration/renewal",
    "GRATUITY_CLAIM": "Gratuity claim processed",
    "CONSENT_TO_OPERATE_RENEWAL": "Consent to Operate renewed under Water/Air Act",
    "EMISSION_TEST": "Stack emission test conducted",
    "EFFLUENT_SAMPLE_TEST": "Effluent sample collected and tested",
    "ENVIRONMENTAL_CLEARANCE": "Environmental clearance obtained/renewed",
    "HAZARDOUS_WASTE_REPORT": "Annual hazardous waste report submitted",
    "STACK_MONITORING": "Continuous stack monitoring report submitted",
}


def generate_events_for_business(department, pattern="active", base_date=None):
    """
    Generate a list of activity events for a business in a department.

    pattern:
        "active"  — regular events, most recent within 6 months
        "dormant" — events stop 6-24 months ago
        "closed"  — events stop 24+ months ago, or explicit closure
    """
    if base_date is None:
        base_date = datetime(2025, 4, 1)

    available_events = EVENT_TYPES.get(department, ["ANNUAL_RETURN_FILED"])
    events = []

    if pattern == "active":
        # Regular events over past 3 years, most recent within 6 months
        num_events = random.randint(8, 20)
        start_date = base_date - timedelta(days=3 * 365)
        for _ in range(num_events):
            event_date = start_date + timedelta(days=random.randint(0, int((base_date - start_date).days)))
            event_type = random.choice(available_events)
            events.append({
                "event_type": event_type,
                "event_date": event_date.strftime("%Y-%m-%d"),
                "description": EVENT_DESCRIPTIONS.get(event_type, "Event recorded"),
                "department": department,
                "status": "COMPLETED",
                "officer": f"Officer-{random.randint(100, 999)}",
            })
        # Ensure at least one recent event
        recent_date = base_date - timedelta(days=random.randint(10, 150))
        event_type = random.choice(available_events)
        events.append({
            "event_type": event_type,
            "event_date": recent_date.strftime("%Y-%m-%d"),
            "description": EVENT_DESCRIPTIONS.get(event_type, "Event recorded"),
            "department": department,
            "status": "COMPLETED",
            "officer": f"Officer-{random.randint(100, 999)}",
        })

    elif pattern == "dormant":
        # Events exist but stopped 6-24 months ago
        num_events = random.randint(5, 12)
        end_date = base_date - timedelta(days=random.randint(180, 720))
        start_date = end_date - timedelta(days=2 * 365)
        for _ in range(num_events):
            event_date = start_date + timedelta(days=random.randint(0, int((end_date - start_date).days)))
            event_type = random.choice(available_events)
            events.append({
                "event_type": event_type,
                "event_date": event_date.strftime("%Y-%m-%d"),
                "description": EVENT_DESCRIPTIONS.get(event_type, "Event recorded"),
                "department": department,
                "status": "COMPLETED",
                "officer": f"Officer-{random.randint(100, 999)}",
            })

    elif pattern == "closed":
        # Very old events, then nothing
        num_events = random.randint(3, 8)
        end_date = base_date - timedelta(days=random.randint(730, 1500))
        start_date = end_date - timedelta(days=2 * 365)
        for _ in range(num_events):
            event_date = start_date + timedelta(days=random.randint(0, int((end_date - start_date).days)))
            event_type = random.choice(available_events)
            events.append({
                "event_type": event_type,
                "event_date": event_date.strftime("%Y-%m-%d"),
                "description": EVENT_DESCRIPTIONS.get(event_type, "Event recorded"),
                "department": department,
                "status": "COMPLETED",
                "officer": f"Officer-{random.randint(100, 999)}",
            })
        # Maybe add a closure event
        if random.random() < 0.4:
            events.append({
                "event_type": "CLOSURE_REPORTED",
                "event_date": end_date.strftime("%Y-%m-%d"),
                "description": "Business closure reported / license surrendered",
                "department": department,
                "status": "COMPLETED",
                "officer": f"Officer-{random.randint(100, 999)}",
            })

    # Sort by date
    events.sort(key=lambda e: e["event_date"])
    return events
