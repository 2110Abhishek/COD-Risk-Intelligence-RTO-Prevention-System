import re
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from app.utils.normalization import normalize_pincode, normalize_phone, normalize_datetime
from app.utils.phone import is_valid_indian_mobile
from app.utils.address import check_placeholder_name, assess_address_structure


FEATURE_COLUMNS = [
    "order_value",
    "num_items",
    "avg_item_value",
    "order_hour",
    "order_weekday",
    "is_weekend",
    "customer_prior_orders",
    "customer_prior_rto",
    "prior_rto_rate",
    "is_first_time",
    "phone_is_valid",
    "pincode_is_valid",
    "has_landmark",
    "name_is_suspicious",
    "address_len",
    "state",
    "courier",
    "utm_source",
]


def extract_order_features(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts structured, leakage-safe features from order data available
    at the exact moment of dispatch decision.
    """
    # Datetime features
    dt = normalize_datetime(order.get("order_datetime")) or datetime.utcnow()
    hour = dt.hour
    weekday = dt.weekday()
    is_weekend = 1 if weekday in (5, 6) else 0

    # Order values
    order_val = float(order.get("order_value", 649.0))
    num_items = max(1, int(order.get("num_items", 1)))
    avg_item_val = round(order_val / num_items, 2)

    # Customer history
    prior_orders = int(order.get("customer_prior_orders", 0))
    prior_rto = int(order.get("customer_prior_rto", 0))
    prior_rto_rate = round(prior_rto / prior_orders, 4) if prior_orders > 0 else 0.0
    is_first_time = 1 if prior_orders == 0 else 0

    # Data quality features
    phone = str(order.get("phone", ""))
    phone_valid = 1 if is_valid_indian_mobile(phone) else 0

    pincode = normalize_pincode(order.get("pincode"))
    pincode_valid = 1 if (pincode and len(pincode) == 6) else 0

    cust_name = str(order.get("customer_name", ""))
    name_check = check_placeholder_name(cust_name)
    name_suspicious = 1 if name_check["is_suspicious"] else 0

    address = str(order.get("address", ""))
    addr_check = assess_address_structure(address)
    has_landmark = 1 if addr_check["has_landmark"] else 0
    address_len = len(address)

    # Categoricals
    state = str(order.get("state") or "UNKNOWN").strip().title()
    courier = str(order.get("courier") or "UNKNOWN").strip()
    utm_source = str(order.get("utm_source") or "direct").strip().lower()

    return {
        "order_value": order_val,
        "num_items": num_items,
        "avg_item_value": avg_item_val,
        "order_hour": hour,
        "order_weekday": weekday,
        "is_weekend": is_weekend,
        "customer_prior_orders": prior_orders,
        "customer_prior_rto": prior_rto,
        "prior_rto_rate": prior_rto_rate,
        "is_first_time": is_first_time,
        "phone_is_valid": phone_valid,
        "pincode_is_valid": pincode_valid,
        "has_landmark": has_landmark,
        "name_is_suspicious": name_suspicious,
        "address_len": address_len,
        "state": state,
        "courier": courier,
        "utm_source": utm_source,
    }
