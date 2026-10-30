import json
import logging
from typing import Dict, Any
import requests
from app.core.settings import settings
from app.llm.base import BaseLLMProvider
from app.llm.prompts import LLM_SYSTEM_PROMPT, format_llm_user_prompt

logger = logging.getLogger(__name__)


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str = settings.llm_api_key, model: str = settings.llm_model):
        self.api_key = api_key
        self.model = model
        self.timeout = settings.llm_timeout_seconds

    def validate_name_and_address(
        self, customer_name: str, address: str, city: str, state: str
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "UNAVAILABLE", "reason": "No API key provided"}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        user_prompt = format_llm_user_prompt(customer_name, address, city, state)
        
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{LLM_SYSTEM_PROMPT}\n\n{user_prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            parsed["status"] = "COMPLETED"
            return parsed
        except Exception as e:
            logger.warning(f"Gemini LLM call failed: {e}")
            return {"status": "UNAVAILABLE", "reason": str(e)}


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str = settings.llm_api_key, model: str = settings.llm_model):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.timeout = settings.llm_timeout_seconds

    def validate_name_and_address(
        self, customer_name: str, address: str, city: str, state: str
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "UNAVAILABLE", "reason": "No API key provided"}

        url = "https://api.openai.com/v1/chat/completions"
        user_prompt = format_llm_user_prompt(customer_name, address, city, state)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            parsed = json.loads(text)
            parsed["status"] = "COMPLETED"
            return parsed
        except Exception as e:
            logger.warning(f"OpenAI LLM call failed: {e}")
            return {"status": "UNAVAILABLE", "reason": str(e)}
