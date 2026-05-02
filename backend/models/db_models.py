"""
SQLAlchemy ORM models for UBID Mesh.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import Base


class DepartmentRecord(Base):
    __tablename__ = "department_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(50), nullable=False, index=True)
    department_display = Column(String(200))
    license_number = Column(String(100))
    business_name = Column(String(500), nullable=False)
    owner_name = Column(String(300))
    pan = Column(String(20), index=True)
    gstin = Column(String(20), index=True)
    phone = Column(String(20))
    address = Column(Text)
    area = Column(String(200))
    city = Column(String(100), index=True)
    pincode = Column(String(10), index=True)
    state = Column(String(50))
    employee_count = Column(Integer)
    established_year = Column(Integer)
    registration_date = Column(String(20))
    status = Column(String(30))
    base_id = Column(Integer)  # Ground truth, for validation only

    # Relationships
    links = relationship("UBIDLink", back_populates="record")
    events = relationship("ActivityEvent", back_populates="record")


class UBID(Base):
    __tablename__ = "ubids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ubid_code = Column(String(30), unique=True, nullable=False, index=True)
    primary_name = Column(String(500))
    primary_owner = Column(String(300))
    primary_address = Column(Text)
    primary_city = Column(String(100))
    primary_pincode = Column(String(10))
    primary_pan = Column(String(20))
    primary_gstin = Column(String(20))
    primary_phone = Column(String(20))
    confidence_score = Column(Float, default=0.0)
    activity_status = Column(String(30), default="UNKNOWN")
    risk_level = Column(String(20), default="LOW")
    risk_score = Column(Float, default=0.0)
    department_count = Column(Integer, default=1)
    record_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    links = relationship("UBIDLink", back_populates="ubid")
    activity_classification = relationship("ActivityClassification", back_populates="ubid", uselist=False)


class UBIDLink(Base):
    __tablename__ = "ubid_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ubid_id = Column(Integer, ForeignKey("ubids.id"), nullable=False)
    record_id = Column(String(50), ForeignKey("department_records.record_id"), nullable=False)
    link_type = Column(String(30), default="AUTO")  # AUTO, MANUAL, REVIEW
    created_at = Column(DateTime, default=datetime.utcnow)

    ubid = relationship("UBID", back_populates="links")
    record = relationship("DepartmentRecord", back_populates="links")


class MatchEvidence(Base):
    __tablename__ = "match_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id_1 = Column(String(50), nullable=False, index=True)
    record_id_2 = Column(String(50), nullable=False, index=True)
    pan_score = Column(Float, default=0.0)
    gstin_score = Column(Float, default=0.0)
    name_score = Column(Float, default=0.0)
    address_score = Column(Float, default=0.0)
    phone_score = Column(Float, default=0.0)
    weighted_score = Column(Float, default=0.0)
    decision = Column(String(30))  # AUTO_LINKED, REVIEW, SEPARATE
    ubid_code = Column(String(30), index=True)
    reviewed = Column(Boolean, default=False)
    review_decision = Column(String(30))  # CONFIRMED, REJECTED, DEFERRED
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(100))


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String(50), ForeignKey("department_records.record_id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_date = Column(String(20), nullable=False)
    description = Column(Text)
    department = Column(String(50))
    status = Column(String(30))
    officer = Column(String(100))

    record = relationship("DepartmentRecord", back_populates="events")


class ActivityClassification(Base):
    __tablename__ = "activity_classifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ubid_id = Column(Integer, ForeignKey("ubids.id"), unique=True, nullable=False)
    classification = Column(String(30))  # ACTIVE, DORMANT, CLOSED
    last_activity_date = Column(String(20))
    days_since_activity = Column(Integer)
    reasoning = Column(Text)  # JSON string with detailed reasoning
    signals_present = Column(Text)  # JSON array
    signals_missing = Column(Text)  # JSON array
    computed_at = Column(DateTime, default=datetime.utcnow)

    ubid = relationship("UBID", back_populates="activity_classification")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("match_evidence.id"), nullable=False)
    decision = Column(String(30), nullable=False)  # CONFIRMED, REJECTED, DEFERRED
    reason = Column(Text)
    decided_by = Column(String(100), default="REVIEWER")
    decided_at = Column(DateTime, default=datetime.utcnow)
    confidence_before = Column(Float)
    confidence_after = Column(Float)


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="SYSTEM")
    ubid_code = Column(String(30))
    record_ids = Column(Text)  # comma-separated
    details = Column(Text)
    category = Column(String(50))  # MERGE, REVIEW, SYSTEM, QUERY


class SystemWeights(Base):
    __tablename__ = "system_weights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pan_weight = Column(Float, default=0.35)
    gstin_weight = Column(Float, default=0.25)
    name_weight = Column(Float, default=0.20)
    address_weight = Column(Float, default=0.10)
    phone_weight = Column(Float, default=0.10)
    auto_link_threshold = Column(Float, default=0.85)
    review_threshold = Column(Float, default=0.60)
    updated_at = Column(DateTime, default=datetime.utcnow)
    update_reason = Column(Text)
