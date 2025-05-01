from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Type


@dataclass
class UserRequest:
    """
    Represents a user's request for a response from a provider.
    """

    messages: List[Dict[str, str]]
    model: str

    provider_name: Optional[str] = None
    response_model: Optional[Type[Any]] = None
    prefill_content: Optional[str] = None
    structured_prefill: bool = False

    stream: bool = False