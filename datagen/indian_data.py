"""
Realistic Indian business data pools for synthetic dataset generation.
Focused on Karnataka state - Bengaluru, Mysuru, Hubli-Dharwad, Mangaluru, etc.
"""

import random
import string

# ============================================================
# BUSINESS NAME COMPONENTS
# ============================================================

BUSINESS_PREFIXES = [
    "Sri", "Shri", "Sree", "New", "Modern", "National", "Royal",
    "Golden", "Silver", "Diamond", "Star", "Prime", "Super",
    "Bharath", "Indian", "Karnataka", "Bangalore", "Mysore",
    "South", "Metro", "City", "United", "Popular", "Classic",
]

BUSINESS_CORE_NAMES = [
    "Lakshmi", "Ganesh", "Venkateshwara", "Krishna", "Rama",
    "Sai", "Mahalakshmi", "Durga", "Hanuman", "Balaji",
    "Nandi", "Kaveri", "Tungabhadra", "Chamundi", "Vijayanagar",
    "Raghavendra", "Manjunath", "Basaveshwara", "Sharada", "Saraswathi",
    "Vinayaka", "Shiva", "Parvathi", "Gouri", "Annapurna",
    "Jayalakshmi", "Padmavathi", "Renuka", "Ambika", "Chandrika",
]

BUSINESS_TYPES = [
    "Industries", "Enterprises", "Trading Co", "Manufacturing",
    "Textiles", "Garments", "Auto Parts", "Engineering Works",
    "Chemicals", "Plastics", "Steel", "Metals", "Electronics",
    "Electrical", "Pharma", "Foods", "Beverages", "Exports",
    "Imports", "Solutions", "Services", "Agencies", "Corporation",
    "Associates", "Traders", "Suppliers", "Distributors", "Works",
    "Factory", "Mills", "Foundry", "Workshop", "Fabricators",
]

BUSINESS_SUFFIXES = [
    "Pvt Ltd", "Private Limited", "LLP", "Ltd", "",
    "& Co", "& Sons", "& Associates", "& Brothers", "",
]

# ============================================================
# OWNER NAMES (South Indian / Karnataka)
# ============================================================

FIRST_NAMES_MALE = [
    "Ramesh", "Suresh", "Mahesh", "Rajesh", "Naresh",
    "Venkatesh", "Ganesh", "Manjunath", "Basavaraj", "Shivakumar",
    "Srinivas", "Raghavendra", "Prashanth", "Naveen", "Anil",
    "Ravi", "Mohan", "Girish", "Harish", "Prakash",
    "Deepak", "Manoj", "Sunil", "Kiran", "Vinod",
    "Jagadish", "Nagesh", "Ashok", "Murali", "Chandrashekar",
    "Gopal", "Satish", "Dinesh", "Umesh", "Ramachandra",
    "Shivanand", "Basavanna", "Mallikarjun", "Siddaramaiah", "Yashwanth",
]

FIRST_NAMES_FEMALE = [
    "Lakshmi", "Saraswathi", "Geetha", "Anitha", "Sunitha",
    "Padma", "Manjula", "Shobha", "Pushpa", "Savitha",
    "Rekha", "Suma", "Divya", "Priya", "Deepa",
    "Kavitha", "Roopa", "Shilpa", "Rashmi", "Pooja",
]

LAST_NAMES = [
    "Gowda", "Shetty", "Reddy", "Naidu", "Rao",
    "Patil", "Kulkarni", "Joshi", "Hegde", "Bhat",
    "Nayak", "Acharya", "Pai", "Kamath", "Shenoy",
    "Murthy", "Sharma", "Gupta", "Kumar", "Swamy",
    "Iyengar", "Iyer", "Pillai", "Menon", "Prasad",
    "Babu", "Das", "Verma", "Singh", "Desai",
]

# ============================================================
# KARNATAKA ADDRESSES
# ============================================================

AREAS_BENGALURU = [
    "Peenya Industrial Area", "Rajajinagar", "Basaveshwaranagar",
    "Malleswaram", "Jayanagar", "JP Nagar", "BTM Layout",
    "Koramangala", "Indiranagar", "Whitefield", "Electronic City",
    "Bommanahalli", "HSR Layout", "Marathahalli", "KR Puram",
    "Yelahanka", "Hebbal", "RT Nagar", "Vijayanagar", "Rajajinagar",
    "Dasarahalli", "Yeshwanthpur", "Nagarbhavi", "Kengeri",
    "Banashankari", "Basavanagudi", "Chickpet", "Majestic",
    "Shivajinagar", "Commercial Street", "Wilson Garden",
    "Hosur Road", "Sarjapur Road", "Mysore Road", "Tumkur Road",
    "Bellary Road", "Old Airport Road", "Outer Ring Road",
    "Bommasandra Industrial Area", "Jigani Industrial Area",
    "Doddaballapur Industrial Area", "Bidadi Industrial Area",
]

AREAS_MYSURU = [
    "Hebbal Industrial Area", "Hootagalli", "Belavadi",
    "Vijayanagar", "Kuvempunagar", "Gokulam", "Saraswathipuram",
    "Jayalakshmipuram", "Lakshmipuram", "Nazarbad",
    "Metagalli Industrial Area", "Belagola Industrial Area",
]

AREAS_HUBLI = [
    "Gokul Road", "Tarihal Industrial Area", "Rayapur",
    "Keshwapur", "Vidyanagar", "Navanagar", "Sattur",
    "Hubli-Dharwad Industrial Area",
]

AREAS_MANGALURU = [
    "Baikampady Industrial Area", "Kavoor", "Bejai",
    "Kankanady", "Hampankatta", "Mangalore SEZ",
    "Bajpe Industrial Area",
]

CITIES = {
    "Bengaluru": {"areas": AREAS_BENGALURU, "pincodes": ["560058", "560010", "560022", "560040", "560034", "560079", "560100", "560048", "560037", "560066", "560003", "560018", "560068", "560099", "560062", "560064"]},
    "Mysuru": {"areas": AREAS_MYSURU, "pincodes": ["570001", "570008", "570010", "570016", "570017", "570018", "570020"]},
    "Hubli": {"areas": AREAS_HUBLI, "pincodes": ["580020", "580021", "580023", "580024", "580025", "580028", "580030"]},
    "Dharwad": {"areas": AREAS_HUBLI[:4], "pincodes": ["580001", "580002", "580003", "580004", "580008"]},
    "Mangaluru": {"areas": AREAS_MANGALURU, "pincodes": ["575001", "575002", "575003", "575004", "575006", "575008"]},
}

STREET_TYPES = [
    "Main Road", "Cross", "Street", "Layout", "Extension",
    "Phase", "Block", "Sector", "Ring Road", "Highway",
]

STATES = ["Karnataka"]

# ============================================================
# DEPARTMENT TYPES
# ============================================================

DEPARTMENTS = [
    "SHOPS_ESTABLISHMENT",
    "FACTORIES",
    "LABOUR",
    "POLLUTION_BOARD",
]

DEPARTMENT_DISPLAY = {
    "SHOPS_ESTABLISHMENT": "Dept. of Shops & Commercial Establishments",
    "FACTORIES": "Dept. of Factories & Boilers",
    "LABOUR": "Dept. of Labour",
    "POLLUTION_BOARD": "Karnataka State Pollution Control Board",
}

# ============================================================
# ID GENERATORS
# ============================================================

def generate_pan():
    """Generate a realistic PAN number: ABCDE1234F"""
    first3 = ''.join(random.choices(string.ascii_uppercase, k=3))
    fourth = random.choice("PCHABGJLFT")  # Entity type
    fifth = random.choice(string.ascii_uppercase)
    digits = ''.join(random.choices(string.digits, k=4))
    last = random.choice(string.ascii_uppercase)
    return f"{first3}{fourth}{fifth}{digits}{last}"


def generate_gstin(pan=None, state_code="29"):
    """Generate GSTIN from PAN. Format: 29ABCDE1234F1Z5"""
    if pan is None:
        pan = generate_pan()
    entity_num = random.choice(["1", "2", "3"])
    check = random.choice(string.ascii_uppercase + string.digits)
    return f"{state_code}{pan}{entity_num}Z{check}"


def generate_phone():
    """Generate Indian mobile number"""
    prefix = random.choice(["98", "97", "96", "95", "94", "93", "91", "90", "88", "87", "86", "85", "84", "83", "82", "81", "80", "79", "78", "77", "76", "75", "74", "73", "72", "71", "70"])
    rest = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{rest}"


def generate_license_number(dept):
    """Generate department-specific license number"""
    prefixes = {
        "SHOPS_ESTABLISHMENT": "KA/SE",
        "FACTORIES": "KA/FAC",
        "LABOUR": "KA/LAB",
        "POLLUTION_BOARD": "KA/PCB",
    }
    prefix = prefixes.get(dept, "KA/GEN")
    year = random.choice(["2019", "2020", "2021", "2022", "2023"])
    num = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}/{year}/{num}"


# ============================================================
# COMPOSITE GENERATORS
# ============================================================

def generate_business_name():
    """Generate a realistic Indian business name"""
    parts = []
    if random.random() < 0.4:
        parts.append(random.choice(BUSINESS_PREFIXES))
    parts.append(random.choice(BUSINESS_CORE_NAMES))
    parts.append(random.choice(BUSINESS_TYPES))
    if random.random() < 0.5:
        parts.append(random.choice(BUSINESS_SUFFIXES))
    return " ".join(p for p in parts if p)


def generate_owner_name():
    """Generate a realistic Karnataka owner name"""
    if random.random() < 0.7:
        first = random.choice(FIRST_NAMES_MALE)
    else:
        first = random.choice(FIRST_NAMES_FEMALE)
    last = random.choice(LAST_NAMES)
    if random.random() < 0.3:
        middle_initial = random.choice(string.ascii_uppercase)
        return f"{first} {middle_initial}. {last}"
    return f"{first} {last}"


def generate_address(city=None):
    """Generate a realistic Karnataka address"""
    if city is None:
        city = random.choice(list(CITIES.keys()))

    city_data = CITIES[city]
    area = random.choice(city_data["areas"])
    pincode = random.choice(city_data["pincodes"])

    door_no = f"{random.randint(1, 999)}"
    if random.random() < 0.3:
        door_no += f"/{random.randint(1, 20)}"

    floor = ""
    if random.random() < 0.3:
        floor = f", {random.choice(['Ground', '1st', '2nd', '3rd'])} Floor"

    street_num = f"{random.randint(1, 20)}th"
    street_type = random.choice(STREET_TYPES)

    return {
        "full": f"No. {door_no}{floor}, {street_num} {street_type}, {area}, {city} - {pincode}, Karnataka",
        "area": area,
        "city": city,
        "pincode": pincode,
        "state": "Karnataka",
    }


def introduce_typo(name):
    """Introduce realistic typos/variations in business names"""
    variations = [
        lambda s: s.replace("Pvt Ltd", "Private Limited"),
        lambda s: s.replace("Private Limited", "Pvt. Ltd."),
        lambda s: s.replace("Industries", "Industires"),
        lambda s: s.replace("Enterprises", "Enterprizes"),
        lambda s: s.replace("Manufacturing", "Mfg"),
        lambda s: s.replace("Engineering", "Engg"),
        lambda s: s.replace("Trading Co", "Trading Company"),
        lambda s: s.replace("Sri", "Shri"),
        lambda s: s.replace("Shri", "Sri"),
        lambda s: s + " " + random.choice(["(Unit-II)", "(Regd)", ""]),
        lambda s: s.replace("  ", " "),
    ]
    result = name
    num_typos = random.randint(1, 2)
    for _ in range(num_typos):
        fn = random.choice(variations)
        result = fn(result)
    return result.strip()


def introduce_address_variation(address_str):
    """Introduce realistic address variations"""
    variations = [
        ("Road", "Rd"),
        ("Street", "St"),
        ("Bengaluru", "Bangalore"),
        ("Mysuru", "Mysore"),
        ("Layout", "Ly"),
        ("Industrial Area", "Indl Area"),
        ("Extension", "Extn"),
        ("Cross", "Cr"),
        ("No.", "No"),
        ("Floor", "Flr"),
    ]
    result = address_str
    for old, new in random.sample(variations, min(2, len(variations))):
        if random.random() < 0.5:
            result = result.replace(old, new)
    return result
