import dataclasses
from typing import Any

from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.data.system_output_type import SystemOutputType


def system_output_to_dict(output: SystemOutput) -> dict[str, Any]:
    """Convert SystemOutput to JSON-serializable dictionary.

    Args:
        output: The SystemOutput to convert

    Returns:
        Dictionary representation suitable for JSON serialization
    """
    result = dataclasses.asdict(output)

    # Convert enum to its value for JSON serialization
    if isinstance(result.get("response_type"), SystemOutputType):
        result["response_type"] = result["response_type"].value

    return result
