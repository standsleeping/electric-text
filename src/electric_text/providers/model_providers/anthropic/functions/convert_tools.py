from typing import Dict, Any, List, Optional


def convert_tools(
    tools: Optional[List[Dict[str, Any]]],
) -> Optional[List[Dict[str, Any]]]:
    """
    Convert the standard tools format to Anthropic's specific format.

    Standard format looks like this:

    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. Omaha, NE"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }

    Anthropic format looks like this:

    {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        }
    }

    Args:
        tools: List of tools in standard format

    Returns:
        List of tools in Anthropic format or None if input is None
    """
    if tools is None:
        return None

    anthropic_tools = []

    for tool in tools:
        anthropic_tool = {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["parameters"],
        }

        anthropic_tools.append(anthropic_tool)

    return anthropic_tools
