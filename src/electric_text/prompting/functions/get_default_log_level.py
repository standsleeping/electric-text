from electric_text.configuration.functions.get_config_value import get_config_value


def get_default_log_level() -> str:
    """Get the default log level from configuration.

    Returns:
        Default log level string from config or fallback default
    """
    return str(get_config_value("logging.level", "ERROR"))
