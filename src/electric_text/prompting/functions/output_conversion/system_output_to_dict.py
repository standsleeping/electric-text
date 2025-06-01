from typing import Any

from electric_text.prompting.data.system_output import SystemOutput


def system_output_to_dict(output: SystemOutput) -> dict[str, Any]:
    """Convert SystemOutput to JSON-serializable dictionary.

    Args:
        output: The SystemOutput to convert

    Returns:
        Dictionary representation suitable for JSON serialization
    """
    # Manual conversion to handle complex union types properly
    result: dict[str, Any] = {
        "response_type": output.response_type.value,
    }

    # Always include all fields, converting manually to avoid union type issues
    if output.text is not None:
        text_output = output.text
        if text_output is not None:
            result["text"] = {"content": text_output.content}
    else:
        result["text"] = None

    if output.data is not None:
        data_output = output.data
        if data_output is not None:
            result["data"] = {
                "data": data_output.data,
                "is_valid": data_output.is_valid,
                "schema_name": data_output.schema_name,
                "validation_error": data_output.validation_error,
            }
    else:
        result["data"] = None

    if output.tool_call is not None:
        tool_call_output = output.tool_call
        if tool_call_output is not None:
            result["tool_call"] = {
                "name": tool_call_output.name,
                "inputs": tool_call_output.inputs,
                "output": tool_call_output.output,
            }
    else:
        result["tool_call"] = None

    return result
