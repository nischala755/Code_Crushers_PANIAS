"""
Seed the database with synthetic data and run the entity resolution pipeline.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal, init_db, Base
from backend.models.db_models import (
    DepartmentRecord, ActivityEvent, SystemWeights, AuditEntry,
)


def seed_database():
    """Generate synthetic data and seed into SQLite."""
    print("=== UBID Mesh Database Seeder ===")

    # Initialize database
    init_db()

    # Drop and recreate all tables for fresh seed
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Generate dataset
        from datagen.generator import generate_dataset
        records, base_businesses = generate_dataset(num_base=120)

        print(f"\nSeeding {len(records)} records into database...")

        # Insert records
        for rec in records:
            db_record = DepartmentRecord(
                record_id=rec["record_id"],
                department=rec["department"],
                department_display=rec["department_display"],
                license_number=rec["license_number"],
                business_name=rec["business_name"],
                owner_name=rec["owner_name"],
                pan=rec["pan"],
                gstin=rec["gstin"],
                phone=rec["phone"],
                address=rec["address"],
                area=rec["area"],
                city=rec["city"],
                pincode=rec["pincode"],
                state=rec["state"],
                employee_count=rec["employee_count"],
                established_year=rec["established_year"],
                registration_date=rec["registration_date"],
                status=rec["status"],
                base_id=rec["_base_id"],
            )
            db.add(db_record)

            # Insert events
            for event in rec.get("events", []):
                db_event = ActivityEvent(
                    record_id=rec["record_id"],
                    event_type=event["event_type"],
                    event_date=event["event_date"],
                    description=event["description"],
                    department=event["department"],
                    status=event["status"],
                    officer=event["officer"],
                )
                db.add(db_event)

        # Insert default system weights
        weights = SystemWeights(
            pan_weight=0.35,
            gstin_weight=0.25,
            name_weight=0.20,
            address_weight=0.10,
            phone_weight=0.10,
            auto_link_threshold=0.85,
            review_threshold=0.60,
            update_reason="Initial default weights",
        )
        db.add(weights)

        # Initial audit entry
        audit = AuditEntry(
            action="SYSTEM_INITIALIZED",
            actor="SYSTEM",
            details=f"Database seeded with {len(records)} records from synthetic data generator",
            category="SYSTEM",
        )
        db.add(audit)

        db.commit()
        print(f"[OK] Seeded {len(records)} department records")

        # Run entity resolution
        print("\nRunning entity resolution pipeline...")
        from backend.engine.resolver import run_entity_resolution
        ubid_count = run_entity_resolution(db)
        print(f"[OK] Created {ubid_count} UBIDs")

        # Run activity inference
        print("\nRunning activity inference...")
        from backend.engine.activity import run_activity_inference
        run_activity_inference(db)
        print("[OK] Activity classification complete")

        # Run risk scoring
        print("\nRunning risk scoring...")
        from backend.engine.risk import run_risk_scoring
        run_risk_scoring(db)
        print("[OK] Risk scoring complete")

        print("\n=== Seeding Complete ===")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
