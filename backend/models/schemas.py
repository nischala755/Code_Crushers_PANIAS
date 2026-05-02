"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---- Registry ----

class RecordBrief(BaseModel):
    record_id: str
    department: str
    department_display: str
    business_name: str
    pan: Optional[str] = ""
    gstin: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    pincode: Optional[str] = ""
    license_number: Optional[str] = ""
    status: Optional[str] = ""

    class Config:
        from_attributes = True


class MatchEvidenceSchema(BaseModel):
    id: int
    record_id_1: str
    record_id_2: str
    pan_score: float
    gstin_score: float
    name_score: float
    address_score: float
    phone_score: float
    weighted_score: float
    decision: Optional[str] = ""
    reviewed: bool = False
    review_decision: Optional[str] = None

    class Config:
        from_attributes = True


class ActivitySchema(BaseModel):
    classification: Optional[str] = "UNKNOWN"
    last_activity_date: Optional[str] = ""
    days_since_activity: Optional[int] = 0
    reasoning: Optional[str] = ""
    signals_present: Optional[str] = "[]"
    signals_missing: Optional[str] = "[]"

    class Config:
        from_attributes = True


class RiskSchema(BaseModel):
    risk_level: str = "LOW"
    risk_score: float = 0.0
    reasons: List[str] = []
    recommendation: str = "No Action"


class UBIDListItem(BaseModel):
    id: int
    ubid_code: str
    primary_name: Optional[str] = ""
    primary_city: Optional[str] = ""
    primary_pincode: Optional[str] = ""
    confidence_score: float = 0.0
    activity_status: Optional[str] = "UNKNOWN"
    risk_level: Optional[str] = "LOW"
    department_count: int = 1
    record_count: int = 1

    class Config:
        from_attributes = True


class UBIDDetail(BaseModel):
    id: int
    ubid_code: str
    primary_name: Optional[str] = ""
    primary_owner: Optional[str] = ""
    primary_address: Optional[str] = ""
    primary_city: Optional[str] = ""
    primary_pincode: Optional[str] = ""
    primary_pan: Optional[str] = ""
    primary_gstin: Optional[str] = ""
    primary_phone: Optional[str] = ""
    confidence_score: float = 0.0
    activity_status: Optional[str] = "UNKNOWN"
    risk_level: Optional[str] = "LOW"
    risk_score: float = 0.0
    department_count: int = 1
    record_count: int = 1
    linked_records: List[RecordBrief] = []
    match_evidence: List[MatchEvidenceSchema] = []
    activity: Optional[ActivitySchema] = None
    risk: Optional[RiskSchema] = None
    events: list = []

    class Config:
        from_attributes = True


# ---- Reviewer ----

class ReviewPairItem(BaseModel):
    evidence_id: int
    record_id_1: str
    record_id_2: str
    name_1: str
    name_2: str
    weighted_score: float
    decision: str
    reviewed: bool = False

    class Config:
        from_attributes = True


class ReviewPairDetail(BaseModel):
    evidence: MatchEvidenceSchema
    record_1: RecordBrief
    record_2: RecordBrief

    class Config:
        from_attributes = True


class ReviewDecisionRequest(BaseModel):
    decision: str  # CONFIRMED, REJECTED, DEFERRED
    reason: Optional[str] = ""
    reviewer: Optional[str] = "REVIEWER"


class ReviewDecisionResponse(BaseModel):
    success: bool
    message: str
    confidence_before: Optional[float] = None
    confidence_after: Optional[float] = None
    weight_changes: Optional[dict] = None


# ---- Query ----

class QueryRequest(BaseModel):
    query: str


class QueryResult(BaseModel):
    ubid_code: str
    business_name: str
    city: str
    pincode: str
    activity_status: str
    risk_level: str
    activity_reasoning: str
    departments: List[str]
    last_activity: Optional[str] = None
    confidence: float = 0.0


class QueryResponse(BaseModel):
    query: str
    interpreted_as: str
    result_count: int
    results: List[QueryResult]


# ---- Graph ----

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "record" or "ubid"
    department: Optional[str] = None
    group: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float
    label: Optional[str] = None


class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# ---- Audit ----

class AuditEntrySchema(BaseModel):
    id: int
    timestamp: Optional[datetime] = None
    action: str
    actor: str = "SYSTEM"
    ubid_code: Optional[str] = ""
    record_ids: Optional[str] = ""
    details: Optional[str] = ""
    category: Optional[str] = ""

    class Config:
        from_attributes = True


# ---- Dashboard ----

class DashboardStats(BaseModel):
    total_records: int = 0
    total_ubids: int = 0
    pending_reviews: int = 0
    active_count: int = 0
    dormant_count: int = 0
    closed_count: int = 0
    department_counts: dict = {}
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    auto_linked: int = 0
    manual_reviewed: int = 0
