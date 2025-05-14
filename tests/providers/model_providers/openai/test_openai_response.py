import copy

from electric_text.providers.model_providers.openai.data.openai_response import (
    OpenAIResponse,
)


def test_openai_response_from_dict(sample_openai_response):
    """Test creating an OpenAIResponse instance from a dictionary."""
    # Create OpenAIResponse instance
    response = OpenAIResponse.from_dict(sample_openai_response)

    # Verify basic fields
    assert response.id == "resp_123"
    assert response.object == "response"
    assert (
        response.created_at == 1747012692
    )  # Not converted to datetime in from_dict anymore
    assert response.status == "completed"
    assert response.model == "gpt-4o-2024-08-06"

    # Verify nested structures
    assert len(response.output) == 1
    message = response.output[0]
    assert message.id == "msg_123"
    assert message.type == "message"
    assert len(message.content) == 1
    assert message.content[0].type == "output_text"
    assert message.content[0].text == '{"key": "value"}'

    # Verify text format
    assert response.text["format"].type == "json_schema"
    assert response.text["format"].name == "test_schema"
    assert response.text["format"].strict is True

    # Verify usage
    assert response.usage.input_tokens == 100
    assert response.usage.output_tokens == 50
    assert response.usage.total_tokens == 150


def test_get_content_text(sample_openai_response_with_content):
    """Test getting content text from the response."""
    # Test with content
    data = copy.deepcopy(sample_openai_response_with_content)
    response = OpenAIResponse.from_dict(data)
    assert response.get_content_text() == "test content"

    # Test with empty output
    data = copy.deepcopy(sample_openai_response_with_content)
    data["output"] = []
    response = OpenAIResponse.from_dict(data)
    assert response.get_content_text() is None

    # Test with empty content
    data = copy.deepcopy(sample_openai_response_with_content)
    data["output"] = [
        {
            "id": "msg_123",
            "type": "message",
            "status": "completed",
            "content": [],
            "role": "assistant",
        }
    ]
    response = OpenAIResponse.from_dict(data)
    assert response.get_content_text() is None
