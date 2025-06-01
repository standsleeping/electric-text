from electric_text.prompting.data.system_input import SystemInput
from electric_text.configuration.functions.get_cached_config import get_cached_config
from electric_text.configuration.functions.get_config_value import get_config_value
from electric_text.prompting.functions.resolve_model_string import resolve_model_string


def resolve_system_input(raw_input: SystemInput) -> SystemInput:
    """Resolve a raw SystemInput by applying configuration defaults and expanding shorthands.

    This function takes a SystemInput with user-provided values and returns a new
    SystemInput with all configuration-based defaults applied and shorthand models expanded.

    Args:
        raw_input: SystemInput with user-provided values (may contain shorthands)

    Returns:
        SystemInput with resolved provider_name, model_name, and config defaults applied
    """
    config = get_cached_config()

    # Construct model string - if model_name already has provider, use it directly
    # Otherwise treat as potential shorthand
    if ":" in raw_input.model_name:
        model_string = raw_input.model_name
    else:
        model_string = raw_input.model_name

    # Resolve model string (expand shorthands and split provider:model)
    provider_name, model_name = resolve_model_string(model_string, config)

    # Apply configuration defaults for log_level if using default
    log_level = raw_input.log_level
    if log_level == "ERROR":  # Default value, check for config override
        log_level = str(get_config_value("logging.level", "ERROR"))

    return SystemInput(
        text_input=raw_input.text_input,
        provider_name=provider_name,
        model_name=model_name,
        log_level=log_level,
        api_key=raw_input.api_key,
        max_tokens=raw_input.max_tokens,
        prompt_name=raw_input.prompt_name,
        stream=raw_input.stream,
        tool_boxes=raw_input.tool_boxes,
    )
