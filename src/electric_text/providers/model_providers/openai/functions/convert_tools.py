from typing import Dict, Any, List, Optional


def convert_tools(
    tools: Optional[List[Dict[str, Any]]],
) -> Optional[List[Dict[str, Any]]]:
    """
    Convert the standard tools format to OpenAI's specific format.

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

    OpenAI format adds the "type": "function" field:

    {
        "type": "function",
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. Chicago, IL"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location", "unit"]
        }
    }

    Args:
        tools: List of tools in standard format

    Returns:
        List of tools in OpenAI format or None if input is None
    """
    if tools is None:
        return None

    openai_tools = []

    for tool in tools:
        openai_tool = {
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        }

        openai_tools.append(openai_tool)

    return openai_tools 