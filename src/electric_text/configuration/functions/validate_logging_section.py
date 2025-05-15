from typing import Dict, Any, List


def validate_logging_section(logging_config: Dict[str, Any]) -> List[str]:
    """Validate the logging section of the configuration.

    Args:
        logging_config: The logging configuration to validate

    Returns:
        List of validation issues
    """
    issues: List[str] = []

    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level = logging_config.get("level")
    if log_level and log_level not in valid_log_levels:
        issues.append(
            f"Invalid log level: {log_level}. Must be one of {valid_log_levels}"
        )

    return issues
