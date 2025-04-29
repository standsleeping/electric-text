from dataclasses import dataclass
from electric_text.providers.base_provider_inputs import BaseProviderInputs


@dataclass
class AnthropicProviderInputs(BaseProviderInputs):
    """Inputs for the Anthropic provider"""
    prefill_content: str | None = None
    structured_prefill: bool = False
