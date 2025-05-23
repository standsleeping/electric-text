from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from electric_text.providers.data.base_provider_inputs import BaseProviderInputs


@dataclass
class OpenAIProviderInputs(BaseProviderInputs):
    """Inputs for the OpenAI provider"""

    messages: list[dict[str, str]]
    user_text_input: str | None = None
    format_schema: Optional[Dict[str, Any]] = None
    strict_schema: bool = False  # Controls whether to enforce strict JSON schema validation
    tools: Optional[List[Dict[str, Any]]] = None  # Tools to be passed to the model
