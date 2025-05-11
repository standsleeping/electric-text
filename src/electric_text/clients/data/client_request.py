from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Type
from electric_text.clients.data.prompt import Prompt


@dataclass
class ClientRequest:
    """
    Represents a client request to be sent to a provider.
    """

    provider_name: str
    model_name: str
    prompt: Prompt
    tools: Optional[List[Dict[str, Any]]] = None
    response_model: Optional[Type[Any]] = None
    max_tokens: Optional[int] = None
