import pytest
import httpx
from starlette.testclient import TestClient
from web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Home" in response.text
    assert '<form hx-post="/submit-prompt"' in response.text


def test_submit_prompt(client):
    response = client.post("/submit-prompt", data={"prompt": "Test prompt"})
    assert response.status_code == 200
    assert 'id="response-area"' in response.text
    assert 'sse-connect="/response-stream?prompt_id=' in response.text
    assert "Test prompt" in response.text


def test_response_stream(client):
    response = client.get("/response-stream?prompt_id=test_prompt&max_events=5")
    chunks = []
    for chunk in response.iter_text(chunk_size=1024):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert "event: SomeEventName" in chunks[0]


@pytest.mark.asyncio
async def test_response_stream_async():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/response-stream?prompt_id=test_prompt&max_events=5"
        )
        content = await response.aread()
        assert "Prompt ID test_prompt" in content.decode()
