import pytest
from typing import List, Optional
from pydantic import BaseModel

from electric_text.prompting.functions.execute_client_request import (
    execute_client_request,
)
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.prompt import Prompt
from electric_text.clients.data.template_fragment import TemplateFragment


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


@pytest.fixture
def client_request():
    """Creates a test client request."""
    prompt = Prompt(
        system_message=[TemplateFragment(text="Test system message")],
        prompt="Test prompt",
    )

    return ClientRequest(
        provider_name="test_provider",
        model_name="test_model",
        prompt=prompt,
    )


# Simple test class that implements the minimum Client interface needed for testing
class ClientForTesting:
    def __init__(self, response_data):
        self.response_data = response_data
        self.call_count = 0
    
    async def generate(self, request):
        self.call_count += 1
        self.last_request = request
        return self.response_data
    
    def stream(self, request):
        async def async_generator():
            self.call_count += 1
            self.last_request = request
            for chunk in self.response_data:
                yield chunk
        return async_generator()


@pytest.mark.asyncio
async def test_execute_client_request_non_streaming(
    sample_client_response_unstructured, client_request, capsys
):
    """Executes a non-streaming client request."""
    # Create test client with response
    test_client = ClientForTesting(sample_client_response_unstructured)

    # Execute request
    await execute_client_request(
        client=test_client,
        request=client_request,
        stream=False,
    )

    # Verify client was called
    assert test_client.call_count == 1
    assert test_client.last_request == client_request

    # Verify output uses content blocks formatting
    captured = capsys.readouterr()
    assert "RESULT (UNSTRUCTURED):\nTest response content" in captured.out


@pytest.mark.asyncio
async def test_execute_client_request_non_streaming_with_model(
    client_request, capsys
):
    """Executes a non-streaming client request with a model class."""
    from electric_text.clients.data.parse_result import ParseResult
    from electric_text.clients.data.client_response import ClientResponse
    
    # Create a parsed model instance
    model_instance = SampleResponseModel(content="test", items=["a", "b"])

    # Create valid parse result
    parse_result = ParseResult(
        raw_content='{"content": "test", "items": ["a", "b"]}',
        parsed_content={"content": "test", "items": ["a", "b"]},
        model=model_instance,
        validation_error=None,
        json_error=None
    )
    response = ClientResponse.from_parse_result(parse_result)
    
    # Create test client with structured response
    test_client = ClientForTesting(response)

    # Execute request
    await execute_client_request(
        client=test_client,
        request=client_request,
        stream=False,
        model_class=SampleResponseModel,
    )

    # Verify client was called
    assert test_client.call_count == 1
    assert test_client.last_request == client_request

    # Verify output
    captured = capsys.readouterr()
    assert "RESULT (STRUCTURED):" in captured.out
    assert '"content": "test"' in captured.out
    assert '"items":' in captured.out


@pytest.mark.asyncio
async def test_execute_client_request_streaming(
    sample_client_response_unstructured, client_request, capsys
):
    """Executes a streaming client request."""
    from electric_text.clients.data.prompt_result import PromptResult
    from electric_text.clients.data.client_response import ClientResponse
    
    # Create streaming chunks
    chunk1 = ClientResponse.from_prompt_result(
        PromptResult(raw_content="Chunk 1", content_blocks=[])
    )
    chunk2 = ClientResponse.from_prompt_result(
        PromptResult(raw_content="Chunk 2", content_blocks=[])
    )
    
    # Create test client with streaming chunks
    test_client = ClientForTesting([chunk1, chunk2])

    # Execute request
    await execute_client_request(
        client=test_client,
        request=client_request,
        stream=True,
    )

    # Verify client was called
    assert test_client.call_count == 1
    assert test_client.last_request == client_request

    # Verify output
    captured = capsys.readouterr()
    assert "PARTIAL RESULT (UNSTRUCTURED): Chunk 1" in captured.out
    assert "PARTIAL RESULT (UNSTRUCTURED): Chunk 2" in captured.out
    assert "FULL RESULT:" in captured.out


@pytest.mark.asyncio
async def test_execute_client_request_streaming_with_tool_calls(
    sample_client_response_with_tool_call, client_request, capsys
):
    """Executes a streaming client request with tool call content blocks."""
    # Create test client with tool call response
    test_client = ClientForTesting([sample_client_response_with_tool_call])

    # Execute request
    await execute_client_request(
        client=test_client,
        request=client_request,
        stream=True,
    )

    # Verify client was called
    assert test_client.call_count == 1
    assert test_client.last_request == client_request

    # Verify output shows formatted content blocks
    captured = capsys.readouterr()
    assert "I'll check the weather for you." in captured.out
    assert "TOOL CALL: get_weather" in captured.out
    assert '"location": "Chicago"' in captured.out