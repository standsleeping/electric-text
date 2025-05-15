import asyncio
import sys

from electric_text.cli.functions.main import main
from electric_text.cli.commands.config import config_command

COMMANDS = {
    "config": config_command,
}

if __name__ == "__main__":
    # Check if a subcommand is specified
    if len(sys.argv) > 1 and sys.argv[1] in COMMANDS:
        # Run the subcommand
        command_name = sys.argv[1]
        command_func = COMMANDS[command_name]
        # Remove the command name from args
        exit_code = command_func(sys.argv[2:])
        sys.exit(exit_code)
    else:
        # Run the default command (process text)
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
