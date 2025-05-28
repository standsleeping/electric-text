from dataclasses import dataclass

from electric_text.prompting.data.system_output_type import SystemOutputType
from electric_text.prompting.data.text_output import TextOutput
from electric_text.prompting.data.data_output import DataOutput
from electric_text.prompting.data.tool_call_output import ToolCallOutput


@dataclass
class SystemOutput:
    """Unified output structure for system responses, designed for JSON serialization."""

    response_type: SystemOutputType
    text: TextOutput | None = None
    data: DataOutput | None = None
    tool_call: ToolCallOutput | None = None
