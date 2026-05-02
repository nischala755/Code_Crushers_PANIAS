"""
Full entity resolution pipeline:
normalize → block → match → cluster → assign UBIDs
"""

import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session
from backend.models.db_models import (
    DepartmentRecord, UBID, UBIDLink, MatchEvidence,
    AuditEntry, SystemWeights,
)
from backend.engine.blocker import build_blocks
from backend.engine.matcher import compute_match_score


def get_current_weights(db: Session):
    """Get current system weights or defaults."""
    sw = db.query(SystemWeights).order_by(SystemWeights.id.desc()).first()
    if sw:
        return {
            "pan": sw.pan_weight,
            "gstin": sw.gstin_weight,
            "name": sw.name_weight,
            "address": sw.address_weight,
            "phone": sw.phone_weight,
        }, {
            "auto_link": sw.auto_link_threshold,
            "review": sw.review_threshold,
        }
    return None, None


def run_entity_resolution(db: Session):
    """
    Execute the full entity resolution pipeline.
    1. Load all department records
    2. Normalize + block
    3. Compute pairwise match scores
    4. Cluster via transitive closure
    5. Assign UBIDs
    6. Store evidence
    """
    print("[ER] Starting entity resolution pipeline...")

    # Load all records
    records = db.query(DepartmentRecord).all()
    record_map = {r.record_id: r for r in records}
    print(f"[ER] Loaded {len(records)} records")

    # Get current weights
    weights, thresholds = get_current_weights(db)

    # Build candidate pairs via blocking
    candidate_pairs = build_blocks(records)
    print(f"[ER] Generated {len(candidate_pairs)} candidate pairs")

    # Compute match scores
    all_evidence = []
    linked_pairs = []  # pairs that are AUTO_LINKED or REVIEW

    for rid1, rid2 in candidate_pairs:
        rec1 = record_map.get(rid1)
        rec2 = record_map.get(rid2)
        if not rec1 or not rec2:
            continue
        # Skip same-department pairs (a business shouldn't be duplicate within one dept for this demo)
        if rec1.department == rec2.department:
            continue

        scores = compute_match_score(rec1, rec2, weights, thresholds)

        evidence = MatchEvidence(
            record_id_1=rid1,
            record_id_2=rid2,
            pan_score=scores["pan_score"],
            gstin_score=scores["gstin_score"],
            name_score=scores["name_score"],
            address_score=scores["address_score"],
            phone_score=scores["phone_score"],
            weighted_score=scores["weighted_score"],
            decision=scores["decision"],
        )
        all_evidence.append(evidence)

        if scores["decision"] in ("AUTO_LINKED", "REVIEW"):
            linked_pairs.append((rid1, rid2, scores["decision"]))

    print(f"[ER] Computed {len(all_evidence)} match scores")
    auto_count = sum(1 for e in all_evidence if e.decision == "AUTO_LINKED")
    review_count = sum(1 for e in all_evidence if e.decision == "REVIEW")
    print(f"[ER] AUTO_LINKED: {auto_count}, REVIEW: {review_count}")

    # Cluster via transitive closure (union-find) for AUTO_LINKED only
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # Build clusters from auto-linked pairs
    for rid1, rid2, decision in linked_pairs:
        if decision == "AUTO_LINKED":
            union(rid1, rid2)

    # Also include single records
    for r in records:
        if r.record_id not in parent:
            parent[r.record_id] = r.record_id

    # Group into clusters
    clusters = defaultdict(set)
    for rid in record_map:
        root = find(rid)
        clusters[root].add(rid)

    print(f"[ER] Formed {len(clusters)} clusters")

    # Clear existing UBIDs and links
    db.query(UBIDLink).delete()
    db.query(UBID).delete()
    db.query(MatchEvidence).delete()

    # Assign UBIDs
    ubid_counter = 0
    for root, members in clusters.items():
        ubid_counter += 1
        ubid_code = f"KA-UBID-{ubid_counter:05d}"

        # Pick primary record (most complete data)
        member_records = [record_map[rid] for rid in members]
        primary = max(member_records, key=lambda r: (
            (1 if r.pan else 0) + (1 if r.gstin else 0) + (1 if r.phone else 0)
        ))

        departments = set(r.department for r in member_records)

        # Compute average confidence from evidence
        relevant_evidence = [
            e for e in all_evidence
            if e.record_id_1 in members and e.record_id_2 in members
            and e.decision in ("AUTO_LINKED", "REVIEW")
        ]
        avg_confidence = 0.0
        if relevant_evidence:
            avg_confidence = sum(e.weighted_score for e in relevant_evidence) / len(relevant_evidence)
        elif len(members) == 1:
            avg_confidence = 1.0  # Single record, full confidence

        ubid = UBID(
            ubid_code=ubid_code,
            primary_name=primary.business_name,
            primary_owner=primary.owner_name,
            primary_address=primary.address,
            primary_city=primary.city,
            primary_pincode=primary.pincode,
            primary_pan=primary.pan,
            primary_gstin=primary.gstin,
            primary_phone=primary.phone,
            confidence_score=round(avg_confidence, 4),
            department_count=len(departments),
            record_count=len(members),
        )
        db.add(ubid)
        db.flush()

        # Update evidence with UBID code
        for ev in relevant_evidence:
            ev.ubid_code = ubid_code

        # Create links
        for rid in members:
            link_type = "AUTO"
            link = UBIDLink(
                ubid_id=ubid.id,
                record_id=rid,
                link_type=link_type,
            )
            db.add(link)

    # Save all evidence
    db.add_all(all_evidence)

    # Audit entry
    audit = AuditEntry(
        action="ENTITY_RESOLUTION_COMPLETE",
        actor="SYSTEM",
        details=f"Processed {len(records)} records into {ubid_counter} UBIDs. "
                f"Auto-linked: {auto_count}, Review: {review_count}",
        category="SYSTEM",
    )
    db.add(audit)

    db.commit()
    print(f"[ER] Entity resolution complete. {ubid_counter} UBIDs created.")
    return ubid_counter
