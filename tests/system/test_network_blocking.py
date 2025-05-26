import pytest
import httpx


def test_blocked_http_request():
    """Unmocked HTTP request is blocked."""

    # This will fail because the autouse fixture blocks all HTTP requests
    with pytest.raises(Exception) as exc_info:
        httpx.get("https://httpbin.org/json")

    assert "RESPX" in str(exc_info.value) and "not mocked" in str(exc_info.value)


@pytest.mark.asyncio
async def test_blocked_async_http_request():
    """Unmocked async HTTP request is blocked."""

    # Also fails for async requests
    with pytest.raises(Exception) as exc_info:
        async with httpx.AsyncClient() as client:
            await client.get("https://httpbin.org/json")

    assert "RESPX" in str(exc_info.value) and "not mocked" in str(exc_info.value)


def test_mocked_request_works(fake_http):
    """Mocked HTTP request works."""

    fake_http.get("https://api.example.com/test").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )

    response = httpx.get("https://api.example.com/test")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
