from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Type
from electric_text.clients.data.prompt import Prompt
from pydantic import BaseModel


@dataclass
class ClientRequest[OutputSchema: BaseModel]:
    """
    Represents a client request to be sent to a provider.
    """

    provider_name: str
    model_name: str
    prompt: Prompt
    output_schema: Type[OutputSchema]
    tools: Optional[List[Dict[str, Any]]] = None
    max_tokens: Optional[int] = None
