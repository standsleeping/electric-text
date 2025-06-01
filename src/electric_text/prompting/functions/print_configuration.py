from typing import Optional

from electric_text.configuration.functions.print_config import print_config


def print_configuration(
    config_path: Optional[str] = None, validate: bool = True
) -> bool:
    """Print and optionally validate the configuration.

    Args:
        config_path: Optional path to configuration file
        validate: Whether to validate the configuration

    Returns:
        Whether there were validation issues
    """
    _, issues = print_config(config_path=config_path, validate=validate)
    return bool(issues)
