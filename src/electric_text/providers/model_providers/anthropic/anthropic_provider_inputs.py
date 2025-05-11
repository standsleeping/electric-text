from dataclasses import dataclass
from electric_text.providers.data.base_provider_inputs import BaseProviderInputs


@dataclass
class AnthropicProviderInputs(BaseProviderInputs):
    """Inputs for the Anthropic provider"""

    messages: list[dict[str, str]] | None = None
    structured_prefill: bool = False
