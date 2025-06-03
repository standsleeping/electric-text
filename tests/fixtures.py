import os
import pytest
import respx
from electric_text.configuration.functions.get_cached_config import (
    get_cached_config,
)


@pytest.fixture(autouse=True)
def fake_http():
    """Block all HTTP requests during tests unless explicitly mocked."""
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def clean_env():
    """Fixture to save and restore environment variables."""
    # Save current environment
    env_backup = os.environ.copy()

    # Clear all ELECTRIC_TEXT_ environment variables
    for key in list(os.environ.keys()):
        if key.startswith("ELECTRIC_TEXT_"):
            del os.environ[key]

    # Clear config cache
    get_cached_config.cache_clear()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(env_backup)

    # Clear config cache again
    get_cached_config.cache_clear()


def sample_http_log_entry():
    """Create a sample HttpLogEntry for testing."""
    from electric_text.providers.logging.data.http_log_entry import HttpLogEntry

    return HttpLogEntry(
        timestamp="2024-01-01T12:00:00Z",
        url="https://api.example.com/chat",
        method="POST",
        request_headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
        },
        request_body={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
        },
        response_status=200,
        response_headers={"Content-Type": "application/json"},
        response_body={"choices": [{"message": {"content": "Hi there!"}}]},
        duration_ms=1222.2,
        provider="openai",
        model="gpt-4",
        error=None,
    )


def minimal_http_log_entry():
    """Create a minimal HttpLogEntry with None values for testing."""
    from electric_text.providers.logging.data.http_log_entry import HttpLogEntry

    return HttpLogEntry(
        timestamp="2024-01-01T12:00:00Z",
        url="https://api.example.com/chat",
        method="GET",
        request_headers={},
        request_body=None,
        response_status=404,
        response_headers={},
        response_body=None,
        duration_ms=100.0,
        provider=None,
        model=None,
        error="HTTP 404",
    )
