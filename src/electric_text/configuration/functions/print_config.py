import os
import sys
from typing import Optional, List, TextIO, Tuple

from electric_text.configuration.data.config import Config
from electric_text.configuration.functions.load_config import load_config
from electric_text.configuration.functions.validate_configuration import (
    validate_configuration,
)


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
