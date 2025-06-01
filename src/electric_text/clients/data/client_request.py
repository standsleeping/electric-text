from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Type
from electric_text.clients.data.prompt import Prompt
from electric_text.clients.data.validation_model import ValidationModel


@dataclass
class ClientRequest[OutputSchema: ValidationModel]:
    """
    Represents a client request to be sent to a provider.
    """

    provider_name: str
    model_name: str
    prompt: Prompt
    output_schema: Type[OutputSchema]
    tools: Optional[List[Dict[str, Any]]] = None
    max_tokens: Optional[int] = None
