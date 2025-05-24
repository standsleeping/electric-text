from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

from electric_text.clients.data import PromptResult, ParseResult

ResponseModel = TypeVar("ResponseModel")


@dataclass
class ClientResponse(Generic[ResponseModel]):
    """
    Represents a unified response from a provider.
    Contains either a raw prompt result or a parsed structured result.
    """

    prompt_result: PromptResult
    parse_result: Optional[ParseResult[ResponseModel]]
