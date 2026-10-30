import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR.parent / "config"
DATA_DIR = BASE_DIR.parent / "data"
MODELS_DIR = BASE_DIR.parent / "models"


class Settings(BaseSettings):
    app_name: str = "COD Risk Intelligence & RTO Prevention"
    app_env: str = "development"
    database_url: str = f"sqlite:///{BASE_DIR / 'cod_risk.db'}"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    timezone: str = "Asia/Kolkata"
    
    # Financial constants (matching PRD & rules.md defaults)
    forward_shipping_cost: float = 65.0
    return_shipping_cost: float = 65.0
    packaging_cost: float = 25.0
    product_cost: float = 180.0
    damage_probability: float = 0.08
    aov_reference: float = 649.0
    gross_margin: float = 0.62
    cac_reference: float = 300.0
    
    # Policy defaults
    ship_as_is_max: float = 0.20
    confirmation_max: float = 0.40
    prepaid_max: float = 0.65
    hold_min: float = 0.65
    prepaid_discount_amount: float = 15.0
    
    # LLM Settings
    llm_enabled: bool = False
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = "gemini-1.5-flash"
    llm_timeout_seconds: int = 8
    
    # File paths
    config_file_path: str = str(CONFIG_DIR / "decision_rules.json")
    model_artifact_path: str = str(MODELS_DIR / "rto_model_pipeline.joblib")
    data_csv_path: str = str(DATA_DIR / "orders_sample.csv")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
