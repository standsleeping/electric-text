import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List, Optional
from pydantic import BaseModel

from electric_text.prompting.functions.execute_client_request import (
    execute_client_request,
)
from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.clients.data.prompt import Prompt
from electric_text.clients.data.template_fragment import TemplateFragment


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


@pytest.fixture
def mock_client():
    """Creates a mock client for testing."""
    client = MagicMock(spec=Client)
    client.provider = MagicMock()
    client.provider.stream_history = MagicMock()
    client.provider.stream_history.get_full_content = MagicMock(
        return_value='{"content": "test", "items": ["a", "b"]}'
    )

    return client


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


@pytest.mark.asyncio
async def test_execute_client_request_non_streaming(
    mock_client, client_request, capsys
):
    """Executes a non-streaming client request."""
    # Create mock response
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.raw_content = "Test response content"
    mock_response.is_valid = False
    mock_response.parsed_model = None

    # Configure mock client
    mock_client.generate = AsyncMock(return_value=mock_response)

    # Execute request
    await execute_client_request(
        client=mock_client,
        request=client_request,
        stream=False,
    )

    # Verify client was called correctly
    mock_client.generate.assert_called_once_with(request=client_request)

    # Verify output
    captured = capsys.readouterr()
    assert "Raw content: Test response content" in captured.out


@pytest.mark.asyncio
async def test_execute_client_request_non_streaming_with_model(
    mock_client, client_request, capsys
):
    """Executes a non-streaming client request with a model class."""
    # Create a parsed model instance
    model_instance = SampleResponseModel(content="test", items=["a", "b"])

    # Create mock response with valid model
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.raw_content = '{"content": "test", "items": ["a", "b"]}'
    mock_response.is_valid = True
    mock_response.parsed_model = model_instance

    # Configure mock client
    mock_client.generate = AsyncMock(return_value=mock_response)

    # Execute request
    await execute_client_request(
        client=mock_client,
        request=client_request,
        stream=False,
        model_class=SampleResponseModel,
    )

    # Verify client was called correctly
    mock_client.generate.assert_called_once_with(request=client_request)

    # Verify output
    captured = capsys.readouterr()
    assert "Result:" in captured.out
    assert "content" in captured.out
    assert "test" in captured.out
    assert "items" in captured.out
    assert "a" in captured.out
    assert "b" in captured.out


@pytest.mark.asyncio
async def test_execute_client_request_streaming(mock_client, client_request, capsys):
    """Executes a streaming client request."""

    # Create async generator for streaming chunks
    async def mock_stream():
        chunk = MagicMock(spec=ClientResponse)
        chunk.raw_content = "Chunk 1"
        chunk.is_valid = False
        chunk.parsed_model = None
        yield chunk

        chunk = MagicMock(spec=ClientResponse)
        chunk.raw_content = "Chunk 2"
        chunk.is_valid = False
        chunk.parsed_model = None
        yield chunk

    # Configure mock client
    mock_client.stream = MagicMock(return_value=mock_stream())

    # Execute request
    await execute_client_request(
        client=mock_client,
        request=client_request,
        stream=True,
    )

    # Verify client was called correctly
    mock_client.stream.assert_called_once_with(request=client_request)

    # Verify output
    captured = capsys.readouterr()
    assert "Raw chunk content: Chunk 1" in captured.out
    assert "Raw chunk content: Chunk 2" in captured.out
    assert "Full content:" in captured.out


@pytest.mark.asyncio
async def test_execute_client_request_streaming_with_model(
    mock_client, client_request, capsys
):
    """Executes a streaming client request with a model class."""
    # Create model instances for chunks
    model_instance1 = SampleResponseModel(content="chunk1")
    model_instance2 = SampleResponseModel(content="chunk2")

    # Create async generator for streaming chunks with models
    async def mock_stream():
        chunk = MagicMock(spec=ClientResponse)
        chunk.raw_content = '{"content": "chunk1"}'
        chunk.is_valid = True
        chunk.parsed_model = model_instance1
        yield chunk

        chunk = MagicMock(spec=ClientResponse)
        chunk.raw_content = '{"content": "chunk2"}'
        chunk.is_valid = True
        chunk.parsed_model = model_instance2
        yield chunk

    # Configure mock client
    mock_client.stream = MagicMock(return_value=mock_stream())

    # Execute request
    await execute_client_request(
        client=mock_client,
        request=client_request,
        stream=True,
        model_class=SampleResponseModel,
    )

    # Verify client was called correctly
    mock_client.stream.assert_called_once_with(request=client_request)

    # Verify output
    captured = capsys.readouterr()
    assert "Valid chunk:" in captured.out
    assert '"content": "chunk1"' in captured.out
    assert '"content": "chunk2"' in captured.out
    assert "Full content:" in captured.out
    assert "JSON:" in captured.out
