import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


from electric_text.configuration.data.config import Config

# Default locations to check for config file
DEFAULT_LOCATIONS = [
    "./config.yaml",
    "~/.electric_text/config.yaml",
    "/etc/electric_text/config.yaml",
]


def load_config(
    config_path: Optional[str] = None, search_locations: list[str] | None = None
) -> Config:
    """Load configuration from YAML file.

    The configuration is loaded in the following order of precedence:
    1. Explicitly provided path
    2. Path from ELECTRIC_TEXT_CONFIG environment variable
    3. Default locations (or custom search_locations if provided):
       - ./config.yaml
       - ~/.electric_text/config.yaml
       - /etc/electric_text/config.yaml

    Args:
        config_path: Optional explicit path to the config file
        search_locations: Optional list of locations to search for config files

    Returns:
        Config instance with loaded configuration
    """
    # Check for config path in environment variable
    env_config_path = os.environ.get("ELECTRIC_TEXT_CONFIG")

    # Determine paths to check in order of priority
    if config_path:
        # Explicit path provided - must exist
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        paths = [path]
    elif env_config_path:
        # Environment variable set - must exist
        path = Path(env_config_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found (from ELECTRIC_TEXT_CONFIG): {env_config_path}"
            )
        paths = [path]
    else:
        # No explicit path - try default locations or custom search locations
        locations = (
            search_locations if search_locations is not None else DEFAULT_LOCATIONS
        )
        paths = [Path(p).expanduser() for p in locations]

    # Find first existing config file
    config_dict: Dict[str, Any] = {}
    for path in paths:
        if path.exists():
            with open(path, "r") as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config is not None:
                    if isinstance(loaded_config, dict):
                        config_dict = loaded_config
                        break
                    else:
                        err: str = f"{path} must contain YAML, not {type(loaded_config).__name__}"
                        raise ValueError(err)

    # Create Config instance from dictionary
    return Config.from_dict(config_dict)
