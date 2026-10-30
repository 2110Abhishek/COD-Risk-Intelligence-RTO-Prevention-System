import re
from typing import Dict, Any


KNOWN_PLACEHOLDERS = {
    "test", "testing", "asdf", "asdfgh", "xyz", "abc", "abc abc", "dummy", "qwerty",
    "sample", "fake", "none", "na", "null", "no address", "unknown"
}


def check_placeholder_name(name: str) -> Dict[str, Any]:
    """
    Deterministic check for obvious placeholder/suspicious names.
    Does NOT reject unusual genuine names.
    """
    clean = re.sub(r"[^\w\s]", "", str(name).lower()).strip()
    
    if not clean or len(clean) < 2:
        return {"is_suspicious": True, "reason": "Name is too short or empty"}
    
    if clean in KNOWN_PLACEHOLDERS:
        return {"is_suspicious": True, "reason": f"Name matches placeholder pattern '{clean}'"}
    
    # Check if name contains digits
    if re.search(r"\d", name):
        return {"is_suspicious": True, "reason": "Name contains numbers"}
    
    # Check for repeated single character (e.g., 'aaaaaa')
    if len(set(clean.replace(" ", ""))) <= 2 and len(clean) > 4:
        return {"is_suspicious": True, "reason": "Name contains repetitive characters"}
    
    return {"is_suspicious": False, "reason": "Valid name"}


def assess_address_structure(address: str) -> Dict[str, Any]:
    """
    Deterministic check for address usability and structure:
    - Obvious placeholders
    - Word count and length
    - Presence of landmarks or locational indicators (Hinglish/English)
    """
    clean = str(address).strip().lower()
    
    if not clean or clean in KNOWN_PLACEHOLDERS or len(clean) < 5:
        return {
            "is_usable": False,
            "has_landmark": False,
            "quality": "INSUFFICIENT",
            "reason": "Address is missing, too short, or contains placeholder text"
        }
    
    landmark_keywords = [
        "near", "opp", "opposite", "behind", "ke paas", "ke saamne", "mandir",
        "temple", "masjid", "chowk", "station", "school", "bank", "road",
        "marg", "nagar", "sector", "society", "apartment", "flat", "gali",
        "house", "h.no", "cross", "left", "right"
    ]
    
    has_landmark = any(kw in clean for kw in landmark_keywords)
    word_count = len(clean.split())
    
    if word_count < 3 and not has_landmark:
        return {
            "is_usable": False,
            "has_landmark": False,
            "quality": "NEEDS_CLARIFICATION",
            "reason": "Address lacks detailed premises or landmark"
        }
    
    return {
        "is_usable": True,
        "has_landmark": has_landmark,
        "quality": "USABLE",
        "reason": "Address contains sufficient locational cues"
    }
