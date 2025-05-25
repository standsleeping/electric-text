from typing import Tuple, Type

from electric_text.clients.data.default_output_schema import DefaultOutputSchema
from pydantic import BaseModel
from electric_text.logging import get_logger
from electric_text.prompting.data.model_result import ModelResult
from electric_text.prompting.data.prompt_config import PromptConfig
from electric_text.prompting.functions.get_prompt_by_name import get_prompt_by_name

logger = get_logger(__name__)


async def get_prompt_config_and_model(
    prompt_name: str,
) -> Tuple[PromptConfig | None, Type[BaseModel]]:
    """Get prompt config and model class if available.

    Args:
        prompt_name: Name of the prompt to use

    Returns:
        Tuple of (prompt_config, model_class)
    """
    prompt_config: PromptConfig | None = get_prompt_by_name(prompt_name)
    if not prompt_config:
        logger.error(f"{prompt_name} prompt config not found")
        return None, DefaultOutputSchema

    model_result: ModelResult = prompt_config.get_model_class()

    return prompt_config, model_result.model_class
