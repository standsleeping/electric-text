from typing import Tuple
from electric_text.prompting.functions.split_model_string import split_model_string
from electric_text.configuration.functions.get_cached_config import get_cached_config
from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)


def parse_provider_model(model_string: str) -> Tuple[str, str]:
    """Parse a model string to get provider and model name.

    Supports multiple formats:
    1. Standard format: "provider:model_name"
    2. Shorthand format: "shorthand" - maps to predefined provider/model pairs

    Args:
        model_string: String in format 'provider:model_name' or shorthand

    Returns:
        Tuple of (provider_name, model_name)
    """
    # Try standard format first (provider:model_name)
    try:
        provider, model_name = split_model_string(model_string)
        return provider, model_name
    except ValueError:
        # If standard format fails, try shorthand lookup
        config = get_cached_config()
        shorthand_models = build_user_shorthand_models(config.shorthands)

        if model_string in shorthand_models:
            provider, model_name = shorthand_models[model_string]
            return provider, model_name

        # If no shorthand found, raise the original error
        raise ValueError(
            f"Invalid model string format: '{model_string}'. "
            f"Expected format 'provider:model_name' or a configured shorthand."
        )
