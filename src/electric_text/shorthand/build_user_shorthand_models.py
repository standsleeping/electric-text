import os
from typing import Dict, Tuple


def build_user_shorthand_models() -> Dict[str, Tuple[str, str]]:
    """Build a lookup dictionary for user-defined model and provider shorthands.

    Scans environment variables for:
    1. [PROVIDER]_PROVIDER_NAME_SHORTHAND=canonical_name++shorthand
       - Maps provider shorthand to canonical provider name

    2. [PROVIDER]_MODEL_SHORTHAND_*=canonical_model++shorthand
       - Maps model shorthand to canonical model name for a specific provider

    Returns:
        Dict mapping shorthand strings to (provider, model) tuples
    """
    # Initialize lookup dictionaries
    provider_shorthands: Dict[str, str] = {}  # shorthand -> canonical provider
    model_lookup: Dict[str, Tuple[str, str]] = {}  # shorthand -> (provider, model)

    # Scan environment variables
    for env_var, value in os.environ.items():
        # Look for provider name shorthands
        if env_var.endswith("_PROVIDER_NAME_SHORTHAND"):
            try:
                canonical_provider, shorthand = value.split("++", 1)
                provider_shorthands[shorthand.strip()] = canonical_provider.strip()
            except ValueError:
                # Skip malformed entries
                continue

        # Look for model shorthands
        elif "_MODEL_SHORTHAND_" in env_var:
            parts = env_var.split("_MODEL_SHORTHAND_", 1)
            if len(parts) != 2:
                continue

            provider_prefix = parts[0].lower()

            try:
                canonical_model, shorthand = value.split("++", 1)
                canonical_model = canonical_model.strip()
                shorthand = shorthand.strip()

                # Extract canonical provider name from prefix
                canonical_provider = provider_prefix

                # Add model shorthand -> (provider, model) mapping
                model_lookup[shorthand] = (canonical_provider, canonical_model)
            except ValueError:
                # Skip malformed entries
                continue

    # Combine lookups: final map contains both provider-only shorthands
    # and specific model shorthands
    combined_lookup: Dict[str, Tuple[str, str]] = {}

    # Process specific model shorthands (these take precedence)
    for shorthand, (provider, model) in model_lookup.items():
        combined_lookup[shorthand] = (provider, model)

    # Provider shorthands don't specify a model, so we set model to None
    # Note that these are lower precedence than specific model shorthands
    for shorthand, provider in provider_shorthands.items():
        # Only add if not already defined as a model shorthand
        if shorthand not in combined_lookup:
            combined_lookup[shorthand] = (provider, "")

    return combined_lookup
