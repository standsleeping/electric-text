import os
from typing import Optional

from electric_text.logging import get_logger

logger = get_logger(__name__)


def resolve_api_key(
    provider_name: str, explicit_api_key: Optional[str] = None
) -> Optional[str]:
    """Resolve API key for a provider, checking both explicit key and environment variables.

    The function will:
    1. First check if an explicit API key was provided
    2. If not, look for an environment variable in the format [PROVIDER_NAME]_API_KEY
       (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY)

    Args:
        provider_name: Name of the provider (e.g., "openai", "anthropic")
        explicit_api_key: Optional API key explicitly provided

    Returns:
        Resolved API key or None if no key is available
    """
    # First check if an explicit API key was provided
    if explicit_api_key:
        return explicit_api_key

    # Then check environment variables
    env_key = f"{provider_name.upper()}_API_KEY"
    env_api_key = os.environ.get(env_key)

    if env_api_key:
        logger.debug(f"Using API key from environment variable {env_key}")
        return env_api_key

    # Return None if no key was found
    return None
