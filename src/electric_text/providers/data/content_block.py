from dataclasses import dataclass
from enum import Enum
from typing import Any, Union


class ContentBlockType(Enum):
    TEXT = "TEXT"
    TOOL_CALL = "TOOL_CALL"


@dataclass
class TextData:
    text: str


@dataclass
class ToolCallData:
    name: str
    input: dict[str, Any]
    input_json_string: str


@dataclass
class ContentBlock:
    type: ContentBlockType
    data: Union[TextData, ToolCallData]
