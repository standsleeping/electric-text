from dataclasses import dataclass
from electric_text.providers.base_provider_inputs import BaseProviderInputs


@dataclass
class OpenAIProviderInputs(BaseProviderInputs):
    """Inputs for the OpenAI provider"""
    pass
