from dataclasses import dataclass
from typing import Optional, List
from .tool_call import ToolCall


@dataclass
class Message:
    role: str
    content: str
    tool_calls: Optional[List[ToolCall]] = None
