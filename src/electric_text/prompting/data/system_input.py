from typing import Optional
from dataclasses import dataclass


@dataclass
class SystemInput:
    """Input parameters for the text processing system.

    This dataclass encapsulates all parameters needed for text processing
    in the electric_text system.

    Args:
        text_input: The text to be processed
        provider_name: The provider to use
        model_name: The model to use
        api_key: Optional API key for providers that require authentication
        max_tokens: Maximum number of tokens to generate
        prompt_name: Optional name of the prompt to use
        stream: Whether to stream the response
        tool_boxes: Optional comma-separated list of tool box names to use
        log_level: Logging level to use
    """

    text_input: str
    provider_name: str
    model_name: str
    log_level: str = "ERROR"
    api_key: Optional[str] = None
    max_tokens: Optional[int] = None
    prompt_name: Optional[str] = None
    stream: bool = False
    tool_boxes: Optional[str] = None