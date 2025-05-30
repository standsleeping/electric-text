from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from electric_text.providers.data.base_provider_inputs import BaseProviderInputs


@dataclass
class AnthropicProviderInputs(BaseProviderInputs):
    """Inputs for the Anthropic provider"""

    messages: list[dict[str, str]]
    structured_prefill: bool = False
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict[str, Any]]] = None