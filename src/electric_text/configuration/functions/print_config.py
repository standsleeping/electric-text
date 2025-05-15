import os
import sys
from typing import Dict, Any, Optional, List, TextIO, Tuple

from electric_text.configuration.data.config import Config
from electric_text.configuration.functions.load_config import load_config


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


def validate_tool_boxes_section(tool_boxes: Dict[str, Any]) -> List[str]:
    """Validate the tool_boxes section of the configuration.

    Args:
        tool_boxes: The tool_boxes configuration to validate

    Returns:
        List of validation issues
    """
    issues: List[str] = []

    for box_name, tools in tool_boxes.items():
        if not isinstance(tools, list):
            issues.append(
                f"Invalid tools list for tool box {box_name}. Must be a list."
            )

    return issues


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
    if provider_defaults and "default_model" not in provider_defaults:
        issues.append("Missing default_model in provider_defaults section")

    # Validate logging configuration
    logging_config = config.logging
    if logging_config:
        issues.extend(validate_logging_section(logging_config))

    # Validate tool box configuration (if present)
    tool_boxes = config.tool_boxes
    if tool_boxes:
        issues.extend(validate_tool_boxes_section(tool_boxes))

    return issues


def print_config(
    config_path: Optional[str] = None,
    output: TextIO = sys.stdout,
    validate: bool = True,
) -> Tuple[Optional[Config], List[str]]:
    """Print the configuration and optionally validate it.

    Args:
        config_path: Optional path to the configuration file
        output: Output stream (defaults to stdout)
        validate: Whether to validate the configuration

    Returns:
        Tuple of (Config object or None if error, List of validation issues)
    """
    # Try to load the configuration
    try:
        if config_path:
            print(f"Loading configuration from: {config_path}", file=output)
            config = load_config(config_path)
        elif os.environ.get("ELECTRIC_TEXT_CONFIG"):
            env_path = os.environ.get("ELECTRIC_TEXT_CONFIG")
            print(
                f"Loading configuration from environment variable ELECTRIC_TEXT_CONFIG: {env_path}",
                file=output,
            )
            config = load_config()
        else:
            print("Loading configuration from default locations:", file=output)
            print("- ./config.yaml", file=output)
            print("- ~/.electric_text/config.yaml", file=output)
            print("- /etc/electric_text/config.yaml", file=output)
            config = load_config()

        # Check if we found a config file
        if not config.raw_config:
            print("\nNo configuration file found!", file=output)
            print("Using default configuration values.", file=output)
            return config, ["No configuration file found"]

        # Validate if requested
        issues = []
        if validate:
            issues = validate_configuration(config)
            if issues:
                print("\nConfiguration validation issues:", file=output)
                for issue in issues:
                    print(f"- {issue}", file=output)
            else:
                print("\nConfiguration is valid.", file=output)

        # Print configuration summary
        print("\nConfiguration Summary:", file=output)

        # Print provider defaults
        print("\nProvider Defaults:", file=output)
        if config.provider_defaults:
            for key, value in config.provider_defaults.items():
                print(f"  {key}: {value}", file=output)
        else:
            print("  None", file=output)

        # Print tool boxes
        print("\nConfigured Tool Boxes:", file=output)
        if config.tool_boxes:
            for box_name, tools in config.tool_boxes.items():
                print(f"  {box_name}: {tools}", file=output)
        else:
            print("  None", file=output)

        # Print logging
        print("\nLogging Configuration:", file=output)
        if config.logging:
            for key, value in config.logging.items():
                print(f"  {key}: {value}", file=output)
        else:
            print("  Default (level: ERROR)", file=output)

        return config, issues

    except Exception as e:
        print(f"\nError loading configuration: {str(e)}", file=output)
        return None, [f"Error loading configuration: {str(e)}"]


