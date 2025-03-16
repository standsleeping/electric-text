from typing import Dict, Any, Literal
import json


OutputFormat = Literal["text", "json"]


def format_result(
    text_input: str,
    result: str,
    output_format: OutputFormat = "text",
) -> str:
    """Format the processed text.

    Args:
        text_input: The text to be processed
        result: The processed text
        output_format: The desired output format ("text" or "json")

    Returns:
        A formatted string representing the processed text
    """
    if output_format == "json":
        data: Dict[str, Any] = {
            "operation": "processing",
            "inputs": {"text_input": text_input},
            "result": result,
        }
        return json.dumps(data, indent=2)
    else:
        return result
