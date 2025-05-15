from typing import Any, Optional, Dict

from electric_text.configuration.functions.get_cached_config import get_cached_config


def get_config_value(
    path: str, default: Any = None, config_path: Optional[str] = None
) -> Any:
    """Get a value from the configuration using a dot notation path.

    Args:
        path: Dot notation path to the configuration value (e.g., "provider_defaults.timeout_seconds")
        default: Default value to return if the path is not found
        config_path: Optional path to the configuration file

    Returns:
        The configuration value at the specified path, or the default value if not found
    """
    config = get_cached_config(config_path)

    # Start with the raw configuration dictionary
    current: Dict[str, Any] = config.raw_config

    # Split the path into components
    components = path.split(".")

    # Traverse the configuration dictionary
    try:
        for component in components:
            # This will raise TypeError if current is not a dict,
            # and KeyError if the component is not found
            current = current[component]
        return current
    except (KeyError, TypeError):
        return default
