import pytest
from unittest.mock import AsyncMock, patch
from models.providers.ollama import ProviderImplementation as OllamaProvider


@pytest.mark.asyncio
async def test_stream():
    provider = OllamaProvider(config={})

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [{"event": "one"}, {"event": "two"}]

    with patch.object(
        provider.client.chat.completions, "create_partial", return_value=mock_stream
    ):
        results = []
        async for chunk in provider.stream("model", [], None):
            results.append(chunk)

        assert len(results) == 2
        assert results[0] == {"event": "one"}
        assert results[1] == {"event": "two"}


@pytest.mark.asyncio
async def test_generate():
    provider = OllamaProvider(config={})
    with patch.object(provider, "generate", AsyncMock(return_value={"event": "one"})):
        result = await provider.generate("model", [], None)
        assert result == {"event": "one"}
