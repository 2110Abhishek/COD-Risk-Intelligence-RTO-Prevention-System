from typing import Dict, Any, Optional
from app.core.settings import settings
from app.llm.provider import GeminiLLMProvider, OpenAICompatibleLLMProvider
from app.utils.address import check_placeholder_name, assess_address_structure


class LLMValidatorService:
    @staticmethod
    def get_provider():
        if settings.llm_provider.lower() in ("gemini", "google"):
            return GeminiLLMProvider()
        return OpenAICompatibleLLMProvider()

    @classmethod
    def validate(
        cls,
        customer_name: str,
        address: str,
        city: str = "",
        state: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validates name and address. If LLM is enabled and configured, queries the LLM.
        Always gracefully falls back to deterministic rules on failure or when LLM is disabled.
        """
        ai_cfg = config.get("ai_config", {}) if config else {}
        is_enabled = ai_cfg.get("enabled", settings.llm_enabled)
        
        # Deterministic baseline
        det_name = check_placeholder_name(customer_name)
        det_addr = assess_address_structure(address)

        fallback_result = {
            "name_quality": "SUSPICIOUS" if det_name["is_suspicious"] else "VALID",
            "address_quality": det_addr["quality"],
            "has_landmark": det_addr["has_landmark"],
            "issues": [det_name["reason"]] if det_name["is_suspicious"] else [],
            "reason": det_addr["reason"],
            "status": "FALLBACK_DETERMINISTIC",
        }

        if not is_enabled:
            return fallback_result

        # Try LLM
        try:
            provider = cls.get_provider()
            llm_res = provider.validate_name_and_address(customer_name, address, city, state)
            if llm_res and llm_res.get("status") == "COMPLETED":
                # Validate schema
                name_q = llm_res.get("name_quality", "VALID")
                addr_q = llm_res.get("address_quality", "USABLE")
                return {
                    "name_quality": name_q if name_q in ("VALID", "SUSPICIOUS", "UNCERTAIN") else "UNCERTAIN",
                    "address_quality": addr_q if addr_q in ("USABLE", "NEEDS_CLARIFICATION", "INSUFFICIENT", "UNCERTAIN") else "UNCERTAIN",
                    "has_landmark": bool(llm_res.get("has_landmark", det_addr["has_landmark"])),
                    "issues": list(llm_res.get("issues", [])),
                    "reason": str(llm_res.get("reason", det_addr["reason"])),
                    "status": "COMPLETED",
                }
            else:
                return fallback_result
        except Exception:
            return fallback_result
