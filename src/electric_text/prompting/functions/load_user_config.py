from electric_text.configuration.functions.load_config import load_config


def load_user_config(config_path: str) -> None:
    """Load user configuration from the specified path.

    This function delegates to the configuration layer to load user config.

    Args:
        config_path: Path to the configuration file to load
    """
    load_config(config_path)
