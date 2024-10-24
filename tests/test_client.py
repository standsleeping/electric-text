import pytest
from unittest.mock import AsyncMock, patch
from models.client import Client


@pytest.mark.asyncio
async def test_generate_stream():
    config = {"stream": True}
    client = Client(provider_name="ollama", config=config)

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [{"event": "one"}, {"event": "two"}]

    with patch.object(client.provider, "generate", return_value=mock_stream):
        results = []
        async for chunk in client.generate("model", [], None):
            results.append(chunk)

        assert len(results) == 2
        assert results[0] == {"event": "one"}
        assert results[1] == {"event": "two"}
