from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    @abstractmethod
    def validate_name_and_address(
        self, customer_name: str, address: str, city: str, state: str
    ) -> Dict[str, Any]:
        """
        Interprets customer name and address quality.
        Returns structured dictionary conforming to expected schema.
        """
        pass
