import pytest
import httpx
from unittest.mock import patch, AsyncMock
from electric_text.providers.model_providers.openai import (
    OpenaiProvider,
)
from electric_text.providers.stream_history import (
    StreamChunkType,
    StreamHistory,
)
from electric_text.clients.data import UserRequest


def test_constructor_with_defaults():
    """Constructor uses reasonable defaults."""
    provider = OpenaiProvider(api_key="test_key")

    assert provider.base_url == "https://api.openai.com/v1/chat/completions"
    assert provider.default_model == "gpt-4o-mini"
    assert provider.timeout == 30.0
    assert provider.client_kwargs["headers"]["Authorization"] == "Bearer test_key"


def test_constructor_with_custom_values():
    """Constructor accepts custom configuration values."""
    provider = OpenaiProvider(
        api_key="custom_key",
        base_url="https://custom.api/v1",
        default_model="custom-model",
        timeout=60.0,
    )

    assert provider.base_url == "https://custom.api/v1"
    assert provider.default_model == "custom-model"
    assert provider.timeout == 60.0
    assert provider.client_kwargs["headers"]["Authorization"] == "Bearer custom_key"


def test_create_payload():
    """Tests create_payload for OpenAI."""
    provider = OpenaiProvider(api_key="test_key")

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    # Test payload
    payload = provider.create_payload(messages, "gpt-4", stream=True)

    assert payload["model"] == "gpt-4"
    assert payload["stream"] is True
    assert len(payload["messages"]) == 2


@pytest.mark.asyncio
async def test_get_client_creates_with_correct_config():
    """Creates an httpx client with the configured timeout and headers."""
    provider = OpenaiProvider(api_key="test_key", timeout=45.0)

    async with provider.get_client() as client:
        assert isinstance(client, httpx.AsyncClient)
        assert client.timeout == httpx.Timeout(45.0)
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["Authorization"] == "Bearer test_key"


@pytest.mark.asyncio
async def test_get_client_closes_after_context():
    """Client is properly closed after exiting the context manager."""
    provider = OpenaiProvider(api_key="test_key")
    client = None

    async with provider.get_client() as c:
        client = c
        assert not client.is_closed

    assert client.is_closed


@pytest.mark.asyncio
async def test_generate_completion_successful_response():
    """Successfully parses a complete response from the API."""
    provider = OpenaiProvider(api_key="test_key")

    mock_request = httpx.Request(
        "POST",
        "http://test",
    )

    mock_response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": "test result"}}]},
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        user_request = UserRequest(
            provider_name="openai",
            messages=[{"role": "user", "content": "test prompt"}],
            model="gpt-4",
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.COMPLETE_RESPONSE
        assert result.chunks[0].content == "test result"
        assert result.get_full_content() == "test result"


@pytest.mark.asyncio
async def test_generate_completion_http_error():
    """Returns StreamHistory with HTTP_ERROR chunk when HTTP request fails."""
    provider = OpenaiProvider(api_key="test_key")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        user_request = UserRequest(
            provider_name="openai",
            messages=[{"role": "user", "content": "test prompt"}],
            model="gpt-4",
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.HTTP_ERROR
        assert result.chunks[0].error == "Complete request failed: Connection failed"
        assert result.chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_completion_missing_content():
    """Returns StreamHistory with FORMAT_ERROR chunk when response is missing required content."""
    provider = OpenaiProvider(api_key="test_key")

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {}  # Missing content field
                }
            ]
        },
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        user_request = UserRequest(
            provider_name="openai",
            messages=[{"role": "user", "content": "test prompt"}],
            model="gpt-4",
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.FORMAT_ERROR
        assert "Failed to parse response" in result.chunks[0].error


@pytest.mark.asyncio
async def test_generate_stream_http_error():
    """Yields StreamHistory with HTTP_ERROR chunk when streaming request fails."""
    provider = OpenaiProvider(api_key="test_key")

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.HTTPError("Stream failed")

        user_request = UserRequest(
            provider_name="openai",
            messages=[{"role": "user", "content": "test prompt"}],
            model="gpt-4",
        )
        histories = []
        async for history in provider.generate_stream(user_request):
            histories.append(history)

        assert len(histories) == 1
        assert isinstance(histories[0], StreamHistory)
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.HTTP_ERROR
        assert histories[0].chunks[0].error == "Stream request failed: Stream failed"
        assert histories[0].chunks[0].raw_line == ""
