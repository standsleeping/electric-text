from typing import List

from electric_text.configuration.functions.get_cached_config import get_cached_config
from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)


def get_model_choices() -> List[str]:
    """Get list of valid model choices for CLI argument parsing.

    Returns:
        List of valid model strings (shorthands + common full model strings)
    """
    config = get_cached_config()
    shorthand_models = build_user_shorthand_models(config.shorthands)
    shorthands = list(shorthand_models.keys())

    # Common full model strings
    common_models = [
        "ollama:llama3.1:8b",
        "anthropic:claude-3-7-sonnet-20250219",
        "openai:gpt-4o-mini",
        "openai:gpt-4o-2024-08-06",
    ]

    # Combine and remove duplicates while preserving order
    all_choices = shorthands + common_models
    return list(dict.fromkeys(all_choices))
