import json
import os
from datetime import datetime
from app.core.database import engine, Base, SessionLocal
from app.models.entities import SystemConfiguration
from app.api.routes.configuration import load_active_config_from_file


def init_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

    db = SessionLocal()
    try:
        active = db.query(SystemConfiguration).filter(SystemConfiguration.configuration_key == "active_policy").first()
        if not active:
            cfg = load_active_config_from_file()
            if cfg:
                active = SystemConfiguration(
                    configuration_key="active_policy",
                    configuration_value=cfg,
                    version=cfg.get("policy_version", "1.0"),
                    updated_by="SYSTEM_INIT"
                )
                db.add(active)
                db.commit()
                print("Seeded active system configuration from decision_rules.json")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
