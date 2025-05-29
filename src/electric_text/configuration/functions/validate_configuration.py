from typing import List

from electric_text.configuration.data.config import Config
from electric_text.configuration.functions.validate_logging_section import (
    validate_logging_section,
)
from electric_text.configuration.functions.validate_http_logging_section import (
    validate_http_logging_section,
)
from electric_text.configuration.functions.validate_tool_boxes_section import (
    validate_tool_boxes_section,
)


def validate_configuration(config: Config) -> List[str]:
    """Validate the configuration and return a list of issues.

    Args:
        config: Configuration to validate

    Returns:
        List of validation issues (empty if configuration is valid)
    """
    issues: List[str] = []

    # Check for required sections
    required_sections = ["provider_defaults", "logging"]
    for section in required_sections:
        if not getattr(config, section, None):
            issues.append(f"Missing required section: {section}")

    # Validate that provider_defaults has default_model
    provider_defaults = config.provider_defaults
    if "default_model" not in provider_defaults:
        issues.append("Missing default_model in provider_defaults section")

    # Validate logging configuration
    logging_config = config.logging
    if logging_config:
        issues.extend(validate_logging_section(logging_config))

    # Validate HTTP logging configuration (if present)
    http_logging_config = config.http_logging
    if http_logging_config:
        issues.extend(validate_http_logging_section(http_logging_config))

    # Validate tool box configuration (if present)
    tool_boxes = config.tool_boxes
    if tool_boxes:
        issues.extend(validate_tool_boxes_section(tool_boxes))

    return issues
