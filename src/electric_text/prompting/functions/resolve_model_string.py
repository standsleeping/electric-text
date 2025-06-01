from electric_text.configuration.data.config import Config
from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)
from electric_text.prompting.functions.split_model_string import split_model_string


def resolve_model_string(model_string: str, config: Config) -> tuple[str, str]:
    """Resolve a model string to provider and model name, handling shorthands.

    Args:
        model_string: String in format 'provider:model_name' or shorthand
        config: Configuration object

    Returns:
        Tuple of (provider_name, model_name)
    """
    # Try standard format first (provider:model_name)
    try:
        provider, model_name = split_model_string(model_string)
        return provider, model_name
    except ValueError:
        # If standard format fails, try shorthand lookup
        shorthand_models = build_user_shorthand_models(config.shorthands)

        if model_string in shorthand_models:
            provider, model_name = shorthand_models[model_string]
            return provider, model_name

        # If no shorthand found, raise the original error
        raise ValueError(
            f"Invalid model string format: '{model_string}'. "
            f"Expected format 'provider:model_name' or a configured shorthand."
        ) 