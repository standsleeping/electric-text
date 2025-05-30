from typing import Optional
from electric_text.prompting.functions.get_prompt_list import get_prompt_list
from electric_text.prompting.data.prompt_config import PromptConfig


def get_prompt_by_name(name: str) -> Optional[PromptConfig]:
    """Get a prompt config by name from the available prompt configs.

    Args:
        name: The name of the prompt config to find

    Returns:
        The prompt config if found, None otherwise
    """
    prompt_configs = get_prompt_list()
    for config in prompt_configs:
        if config.name == name:
            return config
    return None 