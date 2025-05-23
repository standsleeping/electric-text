from electric_text.providers.model_providers.openai.functions.convert_tools import (
    convert_tools,
)


def test_convert_tools():
    """Test converting standard tools format to OpenAI format."""
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

    # Expected OpenAI format
    expected_openai_tools = [
        {
            "type": "function",
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

    # Convert tools
    openai_tools = convert_tools(standard_tools)

    # Check result
    assert openai_tools == expected_openai_tools


def test_convert_tools_none():
    """Test converting None tools."""
    assert convert_tools(None) is None


def test_convert_tools_empty():
    """Test converting empty tools list."""
    assert convert_tools([]) == []


def test_convert_tools_multiple():
    """Test converting multiple tools."""
    # Standard tools format with multiple tools
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
                },
                "required": ["location"],
            },
        },
        {
            "name": "get_forecast",
            "description": "Get the weather forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast",
                        "minimum": 1,
                        "maximum": 7,
                    },
                },
                "required": ["location", "days"],
            },
        },
    ]

    # Expected OpenAI format for multiple tools
    expected_openai_tools = [
        {
            "type": "function",
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                },
                "required": ["location"],
            },
        },
        {
            "type": "function",
            "name": "get_forecast",
            "description": "Get the weather forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast",
                        "minimum": 1,
                        "maximum": 7,
                    },
                },
                "required": ["location", "days"],
            },
        },
    ]

    # Convert tools
    openai_tools = convert_tools(standard_tools)

    # Check result
    assert openai_tools == expected_openai_tools 