import re
from typing import Optional
from app.utils.normalization import normalize_phone


def is_valid_indian_mobile(phone: Optional[str]) -> bool:
    """
    Validates if a phone number matches standard Indian mobile format:
    10 digits starting with 6, 7, 8, or 9.
    """
    clean = normalize_phone(phone)
    if not clean or len(clean) != 10:
        return False
    return bool(re.match(r"^[6-9]\d{9}$", clean))


def mask_phone_number(phone: Optional[str]) -> str:
    """Masks phone number for privacy in UI views (e.g., 98****1234)."""
    clean = normalize_phone(phone)
    if not clean:
        return "N/A"
    if len(clean) == 10:
        return f"{clean[:2]}****{clean[-4:]}"
    elif len(clean) > 4:
        return f"{clean[:2]}****{clean[-2:]}"
    return "****"
