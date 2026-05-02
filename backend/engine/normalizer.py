"""
Name and address normalization for entity resolution.
"""

import re


def normalize_name(name: str) -> str:
    """Clean and normalize a business name for comparison."""
    if not name:
        return ""
    s = name.lower().strip()
    # Remove common suffixes
    removals = [
        r"\bpvt\.?\s*ltd\.?\b",
        r"\bprivate\s+limited\b",
        r"\blimited\b",
        r"\bltd\.?\b",
        r"\bllp\b",
        r"\b&\s*co\.?\b",
        r"\b&\s*sons\b",
        r"\b&\s*associates\b",
        r"\b&\s*brothers\b",
        r"\(unit[-\s]*\w+\)",
        r"\(regd\.?\)",
        r"\(registered\)",
    ]
    for pattern in removals:
        s = re.sub(pattern, "", s, flags=re.IGNORECASE)
    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Remove trailing punctuation
    s = s.rstrip(".,;:-")
    return s


def normalize_address(address: str) -> str:
    """Standardize an address for comparison."""
    if not address:
        return ""
    s = address.lower().strip()
    # Expand common abbreviations
    replacements = {
        r"\brd\b": "road",
        r"\bst\b": "street",
        r"\bblr\b": "bengaluru",
        r"\bbangalore\b": "bengaluru",
        r"\bmysore\b": "mysuru",
        r"\bly\b": "layout",
        r"\bindl\b": "industrial",
        r"\bextn\b": "extension",
        r"\bcr\b": "cross",
        r"\bflr\b": "floor",
        r"\bno\.\b": "no",
        r"\bno\b": "",
    }
    for pattern, replacement in replacements.items():
        s = re.sub(pattern, replacement, s)
    # Remove punctuation except hyphen
    s = re.sub(r"[,./;:]", " ", s)
    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_pincode(address: str) -> str:
    """Extract 6-digit pincode from address."""
    if not address:
        return ""
    match = re.search(r"\b(\d{6})\b", address)
    return match.group(1) if match else ""


def normalize_phone(phone: str) -> str:
    """Normalize phone number to digits only."""
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    # Remove country code if present
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    return digits[-10:] if len(digits) >= 10 else digits
