from electric_text.configuration.functions.get_config_value import get_config_value


def get_default_model() -> str:
    """Get the default model from configuration.
    
    Returns:
        Default model string from config or fallback default
    """
    return str(get_config_value("provider_defaults.default_model", "ollama:llama3.1:8b"))