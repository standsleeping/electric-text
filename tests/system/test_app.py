import pytest
import httpx
from starlette.testclient import TestClient
from web.app import app
from web.domain import SUBMIT_PROMPT, RESPONSE_STREAM


@pytest.fixture
def client():
    return TestClient(app)


def test_submit_prompt(client):
    response = client.post(SUBMIT_PROMPT, data={"prompt": "Test prompt"})
    assert response.status_code == 200
    assert 'id="response-area"' in response.text
    assert f'sse-connect="{RESPONSE_STREAM}?prompt_id=' in response.text
    assert "Test prompt" in response.text


def test_response_stream(client):
    response = client.get(f"{RESPONSE_STREAM}?prompt_id=test_prompt&max_events=5")
    chunks = []
    for chunk in response.iter_text(chunk_size=1024):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert "event: SomeEventName" in chunks[0]


@pytest.mark.asyncio
async def test_response_stream_async():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        get_url = f"{RESPONSE_STREAM}?prompt_id=test_prompt&max_events=5"
        response = await client.get(get_url)
        chunks = []
        async for chunk in response.aiter_text():
            chunks.append(chunk)

        assert len(chunks) > 0
        assert "event: SomeEventName" in "".join(chunks)
        assert "event: StreamClosing" in chunks[-1]
        assert "data: N/A" in chunks[-1]
