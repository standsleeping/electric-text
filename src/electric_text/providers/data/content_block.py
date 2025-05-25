from dataclasses import dataclass
from enum import Enum
from typing import Any, Union


class ContentBlockType(Enum):
    TEXT = "TEXT"
    TOOL_CALL = "TOOL_CALL"


@dataclass
class TextData:
    text: str

    def __str__(self) -> str:
        return self.text


@dataclass
class ToolCallData:
    name: str
    input: dict[str, Any]
    input_json_string: str

    def __str__(self) -> str:
        return f"TOOL CALL: {self.name}\nINPUTS: {self.input_json_string}"


@dataclass
class ContentBlock:
    type: ContentBlockType
    data: Union[TextData, ToolCallData]

    def __str__(self) -> str:
        return str(self.data)
