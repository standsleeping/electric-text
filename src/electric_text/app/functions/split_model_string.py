from typing import Tuple


def split_model_string(model_string: str) -> Tuple[str, str]:
    """Split a model string in the format 'provider:model_name'.

    Args:
        model_string: String in format 'provider:model_name'

    Returns:
        Tuple of (provider_name, model_name)
    """
    # Split provider:model_name into model_name and provider (only split on first colon)
    provider, model_name = model_string.split(":", 1)
    return provider, model_name
