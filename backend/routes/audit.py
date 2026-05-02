"""
Audit log API endpoint.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.db_models import AuditEntry
from backend.models.schemas import AuditEntrySchema

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("/", response_model=list[AuditEntrySchema])
def get_audit_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get audit log entries."""
    query = db.query(AuditEntry)

    if category:
        query = query.filter(AuditEntry.category == category)

    query = query.order_by(AuditEntry.timestamp.desc())
    offset = (page - 1) * page_size
    entries = query.offset(offset).limit(page_size).all()

    return [AuditEntrySchema.model_validate(e) for e in entries]


@router.get("/count")
def count_audit(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AuditEntry)
    if category:
        query = query.filter(AuditEntry.category == category)
    return {"count": query.count()}
