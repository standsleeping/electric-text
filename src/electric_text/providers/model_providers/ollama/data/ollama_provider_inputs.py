from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from electric_text.providers.data.base_provider_inputs import BaseProviderInputs


@dataclass
class OllamaProviderInputs(BaseProviderInputs):
    """Inputs for the Ollama provider"""

    messages: list[dict[str, str]]
    format_schema: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
