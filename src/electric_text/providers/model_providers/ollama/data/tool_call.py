from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ToolCall:
    function: Dict[str, Any]
