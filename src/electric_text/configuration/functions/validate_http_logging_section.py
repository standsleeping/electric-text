from typing import Dict, Any, List


def validate_http_logging_section(http_logging_config: Dict[str, Any]) -> List[str]:
    """Validate the http_logging section of the configuration.

    Args:
        http_logging_config: The HTTP logging configuration to validate

    Returns:
        List of validation issues
    """
    issues: List[str] = []

    # Validate enabled field
    enabled = http_logging_config.get("enabled")
    if enabled is not None and not isinstance(enabled, bool):
        issues.append("http_logging.enabled must be a boolean")

    # Validate log_dir field
    log_dir = http_logging_config.get("log_dir")
    if log_dir is not None and not isinstance(log_dir, str):
        issues.append("http_logging.log_dir must be a string")

    return issues
