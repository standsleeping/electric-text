import pytest
from unittest.mock import AsyncMock, patch
from models.providers.ollama import ProviderImplementation as OllamaProvider


@pytest.mark.asyncio
async def test_generate_stream():
    config = {"stream": True}
    provider = OllamaProvider(config)

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [{"event": "one"}, {"event": "two"}]

    with patch.object(
        provider.client.chat.completions, "create_partial", return_value=mock_stream
    ):
        results = []
        async for chunk in provider.generate("model", [], None):
            results.append(chunk)

        assert len(results) == 2
        assert results[0] == {"event": "one"}
        assert results[1] == {"event": "two"}
