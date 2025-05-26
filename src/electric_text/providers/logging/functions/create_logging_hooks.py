import time
from typing import Any
import httpx

from electric_text.providers.logging.http_logger import HttpLogger
from electric_text.providers.logging.functions.extract_model_from_request import (
    extract_model_from_request,
)


def create_logging_hooks(
    logger: HttpLogger,
    provider: str | None = None,
    model: str | None = None,
) -> dict[str, list[Any]]:
    """Create HTTPX event hooks for request/response logging.

    Args:
        logger: The HttpLogger instance to use
        provider: Provider name for logging
        model: Model name for logging

    Returns:
        Dict of event hooks for httpx.AsyncClient
    """
    request_times: dict[httpx.Request, float] = {}

    async def log_request(request: httpx.Request) -> None:
        """Log request start time."""
        request_times[request] = time.time()

    async def log_response(response: httpx.Response) -> None:
        """Log complete request/response pair."""
        request = response.request
        start_time = request_times.pop(request, time.time())
        duration_ms = (time.time() - start_time) * 1000

        # For streaming responses, read the content
        try:
            await response.aread()
        except Exception:
            # If reading fails, continue with logging
            pass

        # Extract model from request
        extracted_model = extract_model_from_request(request, model)

        # Determine if there was an error
        error = None if response.is_success else f"HTTP {response.status_code}"

        logger.log_request_response(
            request=request,
            response=response,
            duration_ms=duration_ms,
            provider=provider,
            model=extracted_model,
            error=error,
        )

    return {"request": [log_request], "response": [log_response]}
