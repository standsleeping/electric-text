from dataclasses import dataclass
from electric_text.providers.data.base_provider_inputs import BaseProviderInputs


@dataclass
class OpenAIProviderInputs(BaseProviderInputs):
    """Inputs for the OpenAI provider"""

    messages: list[dict[str, str]] | None = None
