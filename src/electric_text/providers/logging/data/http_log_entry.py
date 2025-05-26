from dataclasses import dataclass


@dataclass
class HttpLogEntry:
    """Single HTTP request/response log entry."""

    timestamp: str
    url: str
    method: str
    request_headers: dict[str, str]
    request_body: str | dict[str, object] | None
    response_status: int
    response_headers: dict[str, str]
    response_body: str | dict[str, object] | None
    duration_ms: float
    provider: str | None = None
    model: str | None = None
    error: str | None = None
