"""
Main synthetic dataset generator for UBID Mesh.
Generates 300+ records across 4 departments with realistic overlaps.
"""

import json
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datagen.indian_data import (
    generate_business_name, generate_owner_name, generate_address,
    generate_pan, generate_gstin, generate_phone, generate_license_number,
    introduce_typo, introduce_address_variation,
    DEPARTMENTS, DEPARTMENT_DISPLAY,
)
from datagen.event_generator import generate_events_for_business


def generate_base_businesses(count=100):
    """Generate base business entities (ground truth)."""
    businesses = []
    for i in range(count):
        city = random.choice(["Bengaluru"] * 5 + ["Mysuru"] * 2 + ["Hubli", "Dharwad", "Mangaluru"])
        addr = generate_address(city)
        pan = generate_pan()
        phone = generate_phone()

        businesses.append({
            "base_id": i,
            "business_name": generate_business_name(),
            "owner_name": generate_owner_name(),
            "pan": pan,
            "gstin": generate_gstin(pan),
            "phone": phone,
            "address": addr,
            "employee_count": random.randint(5, 500),
            "established_year": random.randint(1990, 2022),
            "activity_pattern": random.choices(
                ["active", "dormant", "closed"],
                weights=[0.6, 0.25, 0.15],
                k=1
            )[0],
        })
    return businesses


def create_department_record(base_biz, department, record_id, introduce_variations=False):
    """Create a department-specific record from a base business."""
    biz_name = base_biz["business_name"]
    addr_full = base_biz["address"]["full"]
    pan = base_biz["pan"]
    gstin = base_biz["gstin"]
    phone = base_biz["phone"]
    owner = base_biz["owner_name"]

    if introduce_variations:
        # Introduce realistic variations
        if random.random() < 0.6:
            biz_name = introduce_typo(biz_name)
        if random.random() < 0.5:
            addr_full = introduce_address_variation(addr_full)
        if random.random() < 0.1:
            # Occasionally, PAN is missing
            pan = ""
        if random.random() < 0.15:
            # Phone number slightly different (different contact person)
            phone = generate_phone()
        if random.random() < 0.2:
            # GSTIN missing
            gstin = ""

    events = generate_events_for_business(department, base_biz["activity_pattern"])

    return {
        "record_id": f"{department[:3]}-{record_id:05d}",
        "department": department,
        "department_display": DEPARTMENT_DISPLAY[department],
        "license_number": generate_license_number(department),
        "business_name": biz_name,
        "owner_name": owner,
        "pan": pan,
        "gstin": gstin,
        "phone": phone,
        "address": addr_full,
        "area": base_biz["address"]["area"],
        "city": base_biz["address"]["city"],
        "pincode": base_biz["address"]["pincode"],
        "state": "Karnataka",
        "employee_count": base_biz["employee_count"] + random.randint(-10, 10),
        "established_year": base_biz["established_year"],
        "registration_date": f"{random.randint(2018, 2023)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "status": "ACTIVE" if base_biz["activity_pattern"] != "closed" else random.choice(["ACTIVE", "SUSPENDED", "CANCELLED"]),
        "events": events,
        "_base_id": base_biz["base_id"],  # Ground truth link (not exposed to matching)
    }


def generate_dataset(num_base=100):
    """
    Generate the full synthetic dataset.
    ~40% of businesses appear in 2+ departments.
    Target: 300+ total records.
    """
    base_businesses = generate_base_businesses(num_base)
    all_records = []
    record_counter = 0

    for biz in base_businesses:
        # Decide how many departments this business appears in
        r = random.random()
        if r < 0.30:
            # 30%: appears in only 1 department
            num_depts = 1
        elif r < 0.65:
            # 35%: appears in 2 departments
            num_depts = 2
        elif r < 0.85:
            # 20%: appears in 3 departments
            num_depts = 3
        else:
            # 15%: appears in all 4 departments
            num_depts = 4

        selected_depts = random.sample(DEPARTMENTS, num_depts)

        for i, dept in enumerate(selected_depts):
            record_counter += 1
            # First department gets exact data; subsequent ones get variations
            record = create_department_record(
                biz, dept, record_counter,
                introduce_variations=(i > 0)
            )
            all_records.append(record)

    # Add some completely unique records (noise — businesses in only 1 dept with no match)
    noise_count = random.randint(20, 40)
    for _ in range(noise_count):
        record_counter += 1
        noise_biz = generate_base_businesses(1)[0]
        noise_biz["base_id"] = -1  # No ground truth match
        dept = random.choice(DEPARTMENTS)
        record = create_department_record(noise_biz, dept, record_counter, introduce_variations=False)
        record["_base_id"] = -record_counter
        all_records.append(record)

    return all_records, base_businesses


def save_dataset(output_dir=None):
    """Generate and save the dataset to JSON files."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

    os.makedirs(output_dir, exist_ok=True)

    records, base_businesses = generate_dataset(num_base=120)

    # Split by department
    dept_records = {}
    for dept in DEPARTMENTS:
        dept_records[dept] = [r for r in records if r["department"] == dept]

    # Save combined
    with open(os.path.join(output_dir, "all_records.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # Save per-department
    for dept, recs in dept_records.items():
        filename = f"{dept.lower()}.json"
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            json.dump(recs, f, indent=2, ensure_ascii=False)

    # Save ground truth (for validation)
    ground_truth = {}
    for r in records:
        bid = r["_base_id"]
        if bid not in ground_truth:
            ground_truth[bid] = []
        ground_truth[bid].append(r["record_id"])

    with open(os.path.join(output_dir, "ground_truth.json"), "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    # Stats
    print(f"=== Dataset Generation Complete ===")
    print(f"Total records: {len(records)}")
    for dept in DEPARTMENTS:
        print(f"  {DEPARTMENT_DISPLAY[dept]}: {len(dept_records[dept])} records")
    print(f"Base businesses: {len(base_businesses)}")
    multi = sum(1 for v in ground_truth.values() if len(v) > 1)
    print(f"Businesses in 2+ departments: {multi}")
    print(f"Output directory: {output_dir}")

    return records, base_businesses


if __name__ == "__main__":
    save_dataset()
