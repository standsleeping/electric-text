from electric_text.providers.model_providers.ollama.data.message import Message
from electric_text.providers.model_providers.ollama.data.tool_call import ToolCall


def test_message_creation_without_tool_calls():
    """Creates a Message dataclass without tool calls."""
    message = Message(role="assistant", content="Hello, world!")

    assert message.role == "assistant"
    assert message.content == "Hello, world!"
    assert message.tool_calls is None


def test_message_creation_with_tool_calls():
    """Creates a Message dataclass with tool calls."""
    function_data = {"name": "get_weather", "arguments": '{"location":"Seattle"}'}
    tool_call = ToolCall(function=function_data)

    message = Message(
        role="assistant", content="Let me check the weather", tool_calls=[tool_call]
    )

    assert message.role == "assistant"
    assert message.content == "Let me check the weather"
    assert message.tool_calls is not None
    assert len(message.tool_calls) == 1
    assert message.tool_calls[0].function == function_data
