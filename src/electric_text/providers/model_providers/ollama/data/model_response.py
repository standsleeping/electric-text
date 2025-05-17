from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from .message import Message
from .tool_call import ToolCall


@dataclass
class ModelResponse:
    model: str
    created_at: datetime
    message: Message
    done_reason: str
    done: bool
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int
    raw_line: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any], raw_line: str) -> "ModelResponse":
        # Convert created_at string to datetime
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))

        # Convert message data
        msg_data = data["message"]
        tool_calls = None
        if "tool_calls" in msg_data:
            tool_calls = [
                ToolCall(function=tc["function"]) for tc in msg_data["tool_calls"]
            ]

        message = Message(
            role=msg_data["role"],
            content=msg_data["content"],
            tool_calls=tool_calls,
        )

        return cls(
            model=data["model"],
            created_at=created_at,
            message=message,
            done_reason=data["done_reason"],
            done=data["done"],
            total_duration=data["total_duration"],
            load_duration=data["load_duration"],
            prompt_eval_count=data["prompt_eval_count"],
            prompt_eval_duration=data["prompt_eval_duration"],
            eval_count=data["eval_count"],
            eval_duration=data["eval_duration"],
            raw_line=raw_line,
        )
