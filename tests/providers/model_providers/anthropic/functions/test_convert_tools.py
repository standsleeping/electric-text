from electric_text.providers.model_providers.anthropic.functions.convert_tools import (
    convert_tools,
)


def test_convert_tools():
    """Test converting standard tools format to Anthropic format."""
    # Standard tools format
    standard_tools = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]

    # Expected Anthropic format
    expected_anthropic_tools = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]

    # Convert tools
    anthropic_tools = convert_tools(standard_tools)

    # Check result
    assert anthropic_tools == expected_anthropic_tools


def test_convert_tools_none():
    """Test converting None tools."""
    assert convert_tools(None) is None


def test_convert_tools_empty():
    """Test converting empty tools list."""
    assert convert_tools([]) == []
