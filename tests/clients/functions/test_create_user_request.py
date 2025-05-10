from electric_text.clients.functions.create_user_request import create_user_request
from electric_text.clients.data.user_request import UserRequest
from electric_text.clients import build_simple_prompt, convert_prompt_to_messages


def test_create_with_system_and_text():
    """Test creating a request with system message and text input."""
    system_message = "You are a helpful assistant."
    text_input = "Tell me a joke."

    # Expected messages after conversion
    expected_prompt = build_simple_prompt(system_message, text_input)
    expected_messages = convert_prompt_to_messages(expected_prompt)

    request = create_user_request(
        model_name="gpt-4",
        provider_name="openai",
        system_message=system_message,
        text_input=text_input,
    )

    assert isinstance(request, UserRequest)
    assert request.messages == expected_messages
    assert request.model == "gpt-4"
    assert request.provider_name == "openai"
    assert request.response_model is None
    assert not request.stream
    assert request.max_tokens is None
    assert request.tool_boxes == []
    assert request.tools == []


def test_create_with_response_model_and_stream():
    """Test creating a request with a response model and stream enabled."""

    class DummyModel:
        pass

    request = create_user_request(
        model_name="claude-3",
        provider_name="anthropic",
        response_model=DummyModel,
        stream=True,
        system_message="You are a helpful assistant.",
        text_input="Tell me a joke.",
    )

    formed_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]

    assert isinstance(request, UserRequest)
    assert request.messages == formed_messages
    assert request.model == "claude-3"
    assert request.provider_name == "anthropic"
    assert request.response_model == DummyModel
    assert request.stream
    assert request.max_tokens is None
    assert request.tool_boxes == []
    assert request.tools == []


def test_create_with_max_tokens():
    """Test creating a request with max_tokens specified."""
    system_message = "You are a helpful assistant."
    text_input = "Tell me a joke."
    max_tokens = 100

    request = create_user_request(
        model_name="claude-3",
        provider_name="anthropic",
        system_message=system_message,
        text_input=text_input,
        max_tokens=max_tokens,
    )

    formed_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]

    assert isinstance(request, UserRequest)
    assert request.messages == formed_messages
    assert request.model == "claude-3"
    assert request.provider_name == "anthropic"
    assert request.max_tokens == max_tokens
    assert request.tool_boxes == []
    assert request.tools == []


def test_empty_input_handling():
    """Test creating a request with None values for system_message and text_input."""
    request = create_user_request(
        model_name="gpt-4",
        provider_name="openai",
        system_message=None,
        text_input=None,
    )

    # Should handle None values without errors
    assert isinstance(request, UserRequest)

    # Expected messages for empty prompt
    expected_prompt = build_simple_prompt("You are a helpful assistant.", "")
    expected_messages = convert_prompt_to_messages(expected_prompt)

    assert request.messages == expected_messages
    assert request.max_tokens is None
    assert request.tool_boxes == []
    assert request.tools == []


def test_create_with_tool_boxes(temp_tool_configs_dir):
    """Test creating a request with tool boxes specified."""
    request = create_user_request(
        model_name="gpt-4",
        provider_name="openai",
        system_message="You are a helpful assistant.",
        text_input="Tell me the weather.",
        tool_boxes=["test_box"],
    )

    assert isinstance(request, UserRequest)
    assert request.model == "gpt-4"
    assert request.provider_name == "openai"
    assert request.tool_boxes == ["test_box"]

    # Tools should be loaded
    assert len(request.tools) == 2
    tool_names = [tool["name"] for tool in request.tools]
    assert "test_tool1" in tool_names
    assert "test_tool2" in tool_names


def test_create_with_explicit_tools():
    """Test creating a request with explicitly provided tools."""
    tool_box_names = ["meteorology"]
    explicit_tools = [{"name": "custom_tool", "description": "Custom tool"}]

    request = create_user_request(
        model_name="gpt-4",
        provider_name="openai",
        system_message="You are a helpful assistant.",
        text_input="Tell me the weather.",
        tool_boxes=tool_box_names,
        tools=explicit_tools,
    )

    assert isinstance(request, UserRequest)
    assert request.model == "gpt-4"
    assert request.provider_name == "openai"
    assert request.tool_boxes == tool_box_names
    assert request.tools == explicit_tools
