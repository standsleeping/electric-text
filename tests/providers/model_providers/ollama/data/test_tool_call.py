from electric_text.providers.model_providers.ollama.data.tool_call import ToolCall


def test_tool_call_creation():
    """Creates a ToolCall dataclass with function parameter."""
    function_data = {"name": "get_weather", "arguments": '{"location":"Seattle"}'}

    tool_call = ToolCall(function=function_data)

    assert tool_call.function == function_data
    assert tool_call.function["name"] == "get_weather"
    assert tool_call.function["arguments"] == '{"location":"Seattle"}'
