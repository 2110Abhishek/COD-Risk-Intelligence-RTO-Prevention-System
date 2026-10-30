import re
from datetime import datetime
from typing import Optional, Any


def normalize_pincode(pincode: Any) -> Optional[str]:
    """
    Normalizes pincode to a clean 6-digit string.
    Strips trailing .0 from floats, spaces, and non-digit characters.
    """
    if pincode is None:
        return None
    s = str(pincode).strip()
    if s.endswith(".0"):
        s = s[:-2]
    # Remove any non-digits
    digits = re.sub(r"\D", "", s)
    if len(digits) == 6:
        return digits
    return digits if digits else None


def normalize_phone(phone: Any) -> Optional[str]:
    """
    Normalizes Indian phone number to 10 digits.
    Removes country code (+91, 91), leading zeros, and punctuation.
    """
    if phone is None:
        return None
    s = str(phone).strip()
    if s.endswith(".0"):
        s = s[:-2]
    digits = re.sub(r"\D", "", s)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    return digits


def normalize_datetime(dt_val: Any) -> Optional[datetime]:
    """Parses various datetime string formats into UTC datetime object."""
    if dt_val is None:
        return None
    if isinstance(dt_val, datetime):
        return dt_val
    s = str(dt_val).strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def normalize_text(text: Any) -> str:
    """Strips whitespace and normalizes consecutive spaces."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()
