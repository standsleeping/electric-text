from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Type


@dataclass
class ProviderRequest:
    """
    Represents a request to be sent to a provider.
    """

    provider_name: str
    model_name: str
    prompt_text: str
    system_messages: Optional[List[str]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    response_model: Optional[Type[Any]] = None
    max_tokens: Optional[int] = None
