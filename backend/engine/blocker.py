"""
Blocking strategies to reduce pairwise comparisons.
Groups records into candidate blocks using multiple keys.
"""

from collections import defaultdict
from backend.engine.normalizer import normalize_name, normalize_phone, extract_pincode


def build_blocks(records):
    """
    Create candidate pair blocks using multiple blocking keys.
    Returns a set of candidate pairs (record_id tuples).
    """
    blocks = defaultdict(set)

    for rec in records:
        rid = rec.record_id
        name = normalize_name(rec.business_name)
        pan = (rec.pan or "").strip().upper()
        phone = normalize_phone(rec.phone or "")
        pincode = rec.pincode or extract_pincode(rec.address or "")

        # Block 1: First 4 chars of normalized name + pincode
        if len(name) >= 4 and pincode:
            key1 = f"NP:{name[:4]}:{pincode}"
            blocks[key1].add(rid)

        # Block 2: PAN (first 8 chars — most discriminative portion)
        if len(pan) >= 8:
            key2 = f"PAN:{pan[:8]}"
            blocks[key2].add(rid)

        # Block 3: Full PAN match
        if len(pan) == 10:
            key3 = f"PANFULL:{pan}"
            blocks[key3].add(rid)

        # Block 4: Phone number
        if len(phone) >= 10:
            key4 = f"PHONE:{phone}"
            blocks[key4].add(rid)

        # Block 5: First 3 chars of name + city
        city = (rec.city or "").lower().strip()
        if len(name) >= 3 and city:
            key5 = f"NC:{name[:3]}:{city}"
            blocks[key5].add(rid)

    # Generate candidate pairs from blocks
    candidate_pairs = set()
    for block_key, members in blocks.items():
        members_list = list(members)
        for i in range(len(members_list)):
            for j in range(i + 1, len(members_list)):
                pair = tuple(sorted([members_list[i], members_list[j]]))
                candidate_pairs.add(pair)

    return candidate_pairs
