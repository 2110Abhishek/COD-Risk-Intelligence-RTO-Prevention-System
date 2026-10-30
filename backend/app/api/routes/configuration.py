import json
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.settings import settings
from app.models.entities import SystemConfiguration, AuditLog
from app.schemas.schemas import FullConfiguration

router = APIRouter(prefix="/config", tags=["Configuration"])


def load_active_config_from_file() -> dict:
    config_path = settings.config_file_path
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config_to_file(config_data: dict):
    config_path = settings.config_file_path
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)


@router.get("", response_model=FullConfiguration)
def get_active_configuration(db: Session = Depends(get_db)):
    """Returns the currently active operational rules and thresholds."""
    # Check DB first
    db_config = db.query(SystemConfiguration).filter(SystemConfiguration.configuration_key == "active_policy").first()
    if db_config:
        return db_config.configuration_value

    # Fallback to config file
    file_cfg = load_active_config_from_file()
    if file_cfg:
        return file_cfg

    raise HTTPException(status_code=404, detail="Configuration not found")


@router.put("", response_model=FullConfiguration)
def update_configuration(new_config: FullConfiguration, db: Session = Depends(get_db)):
    """
    Validates and updates business policy configuration.
    Records version audit trail without modifying previous historical decisions.
    """
    cfg_dict = new_config.model_dump()
    
    # Validate threshold ordering
    th = cfg_dict["risk_thresholds"]
    if not (0 <= th["ship_as_is_max"] <= th["confirmation_max"] <= th["prepaid_max"] <= th["hold_min"] <= 1):
        raise HTTPException(
            status_code=400,
            detail="Invalid threshold ordering. Must satisfy: 0 <= ship_as_is_max <= confirmation_max <= prepaid_max <= hold_min <= 1"
        )

    # Increment version
    current_ver = float(cfg_dict.get("policy_version", "1.0"))
    new_ver = f"{round(current_ver + 0.1, 1)}"
    cfg_dict["policy_version"] = new_ver

    # Fetch previous
    db_config = db.query(SystemConfiguration).filter(SystemConfiguration.configuration_key == "active_policy").first()
    prev_val = db_config.configuration_value if db_config else load_active_config_from_file()

    if db_config:
        db_config.configuration_value = cfg_dict
        db_config.version = new_ver
        db_config.updated_at = datetime.utcnow()
    else:
        db_config = SystemConfiguration(
            configuration_key="active_policy",
            configuration_value=cfg_dict,
            version=new_ver,
            updated_by="ADMIN"
        )
        db.add(db_config)

    # Save to disk as well
    save_config_to_file(cfg_dict)

    # Record Audit Log
    audit = AuditLog(
        actor="ADMIN",
        action="UPDATE_CONFIGURATION",
        entity_type="SYSTEM_CONFIGURATION",
        entity_id="active_policy",
        previous_value=prev_val,
        new_value=cfg_dict,
        reason=f"Updated operational risk thresholds and assumptions to version {new_ver}"
    )
    db.add(audit)
    db.commit()

    return cfg_dict


@router.get("/history")
def get_configuration_history(db: Session = Depends(get_db)):
    """Returns audit log history of all configuration updates."""
    logs = db.query(AuditLog).filter(AuditLog.entity_type == "SYSTEM_CONFIGURATION").order_by(AuditLog.created_at.desc()).all()
    return [
        {
            "id": l.id,
            "actor": l.actor,
            "action": l.action,
            "previous_value": l.previous_value,
            "new_value": l.new_value,
            "reason": l.reason,
            "timestamp": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
