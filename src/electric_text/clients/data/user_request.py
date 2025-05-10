from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Type


@dataclass
class UserRequest:
    """
    Represents a user's request for a response from a provider.
    """

    provider_name: str
    model: str
    messages: List[Dict[str, str]]
    tool_boxes: List[str] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)

    response_model: Optional[Type[Any]] = None
    prefill_content: Optional[str] = None
    structured_prefill: bool = False

    max_tokens: Optional[int] = None
    stream: bool = False
