import argparse
from typing import List, Optional

from electric_text.prompting.functions.print_configuration import print_configuration


def config_command(args: Optional[List[str]] = None) -> int:
    """Run the configuration command.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        prog="electric_text config",
        description="Show and validate the electric_text configuration",
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to configuration file",
    )

    parser.add_argument(
        "--no-validate",
        "-n",
        action="store_true",
        help="Disable validation",
    )

    parsed_args = parser.parse_args(args)

    has_issues = print_configuration(
        config_path=parsed_args.config, validate=not parsed_args.no_validate
    )

    # Return error code if there are issues
    return 1 if has_issues else 0
