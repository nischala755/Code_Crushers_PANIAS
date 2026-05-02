"""
Graph data API endpoint.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.db_models import UBID, UBIDLink, MatchEvidence, DepartmentRecord
from backend.models.schemas import GraphData, GraphNode, GraphEdge

router = APIRouter(prefix="/api/graph", tags=["Graph"])

DEPT_COLORS = {
    "SHOPS_ESTABLISHMENT": "#3498db",
    "FACTORIES": "#e67e22",
    "LABOUR": "#2ecc71",
    "POLLUTION_BOARD": "#9b59b6",
}


@router.get("/", response_model=GraphData)
def get_graph_data(
    limit: int = Query(30, ge=5, le=100),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """Get graph nodes and edges for visualization."""
    # Get UBIDs with multiple records (interesting clusters)
    ubids = db.query(UBID).filter(UBID.record_count > 1).order_by(
        UBID.record_count.desc()
    ).limit(limit).all()

    nodes = []
    edges = []
    seen_records = set()

    for ubid in ubids:
        # UBID node
        nodes.append(GraphNode(
            id=ubid.ubid_code,
            label=ubid.primary_name or ubid.ubid_code,
            type="ubid",
            group=ubid.ubid_code,
        ))

        # Get linked records
        links = db.query(UBIDLink).filter(UBIDLink.ubid_id == ubid.id).all()
        for link in links:
            if link.record_id not in seen_records:
                rec = db.query(DepartmentRecord).filter(
                    DepartmentRecord.record_id == link.record_id
                ).first()
                if rec:
                    nodes.append(GraphNode(
                        id=rec.record_id,
                        label=f"{rec.business_name[:30]}",
                        type="record",
                        department=rec.department,
                        group=ubid.ubid_code,
                    ))
                    seen_records.add(link.record_id)

            # Edge from record to UBID
            edges.append(GraphEdge(
                source=link.record_id,
                target=ubid.ubid_code,
                weight=ubid.confidence_score,
                label=f"{ubid.confidence_score:.0%}",
            ))

        # Get match evidence edges between records
        evidence = db.query(MatchEvidence).filter(
            MatchEvidence.ubid_code == ubid.ubid_code,
            MatchEvidence.weighted_score >= min_score,
        ).all()

        for ev in evidence:
            edges.append(GraphEdge(
                source=ev.record_id_1,
                target=ev.record_id_2,
                weight=ev.weighted_score,
                label=f"{ev.weighted_score:.0%}",
            ))

    return GraphData(nodes=nodes, edges=edges)
