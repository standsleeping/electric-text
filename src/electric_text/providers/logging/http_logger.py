import json
import time
from datetime import datetime
from pathlib import Path
import httpx

from electric_text.providers.logging.data.http_log_entry import HttpLogEntry
from electric_text.providers.logging.functions.http_log_entry_to_dict import (
    http_log_entry_to_dict,
)


class HttpLogger:
    """Logger for HTTP requests and responses."""

    def __init__(
        self,
        log_dir: Path | None = None,
        enabled: bool = True,
        save_to_file: bool = True,
    ):
        """Initialize the HTTP logger.

        Args:
            log_dir: Directory to save logs (defaults to ./http_logs)
            enabled: Whether logging is enabled
            save_to_file: Whether to save logs to files
        """
        self.enabled = enabled
        self.save_to_file = save_to_file
        self.log_dir = log_dir or Path("./http_logs")
        self.entries: list[HttpLogEntry] = []

        if self.save_to_file and self.enabled:
            self.log_dir.mkdir(exist_ok=True)

    def log_request_response(
        self,
        request: httpx.Request,
        response: httpx.Response,
        duration_ms: float,
        provider: str | None = None,
        model: str | None = None,
        error: str | None = None,
    ) -> HttpLogEntry | None:
        """Log an HTTP request/response pair.

        Args:
            request: The httpx request
            response: The httpx response
            duration_ms: Request duration in milliseconds
            provider: Provider name (e.g., "anthropic")
            model: Model name (e.g., "claude-3-sonnet")
            error: Any error that occurred

        Returns:
            The created log entry
        """
        if not self.enabled:
            return None

        # Parse request body
        request_body = None
        if request.content:
            try:
                request_body = json.loads(request.content.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_body = request.content.decode()

        # Parse response body
        response_body = None
        try:
            response_body = response.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            response_body = response.text

        entry = HttpLogEntry(
            timestamp=datetime.now().isoformat(),
            method=request.method,
            url=str(request.url),
            request_headers=dict(request.headers),
            request_body=request_body,
            response_status=response.status_code,
            response_headers=dict(response.headers),
            response_body=response_body,
            duration_ms=duration_ms,
            provider=provider,
            model=model,
            error=error,
        )

        self.entries.append(entry)

        if self.save_to_file:
            self.save_entry(entry)

        return entry

    def save_entry(self, entry: HttpLogEntry) -> None:
        """Save a log entry to file."""
        timestamp = int(time.time())
        name = f"{timestamp}_{entry.provider or 'unknown'}_{entry.method.lower()}.json"
        filepath = self.log_dir / name

        with open(filepath, "w") as f:
            json.dump(http_log_entry_to_dict(entry), f, indent=2)

    def clear(self) -> None:
        """Clear all logged entries."""
        self.entries.clear()
