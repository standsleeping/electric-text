"""Logging wrapper for httpx AsyncClient using event hooks."""

from typing import Any
import httpx

from electric_text.providers.logging.http_logger import HttpLogger
from electric_text.providers.logging.functions.create_logging_hooks import (
    create_logging_hooks,
)


class LoggingAsyncClient:
    """AsyncClient wrapper that logs all requests and responses using event hooks."""

    def __init__(
        self,
        logger: HttpLogger,
        provider: str | None = None,
        model: str | None = None,
        **client_kwargs: Any,
    ) -> None:
        """Initialize the logging client.

        Args:
            logger: The HttpLogger instance to use
            provider: Provider name for logging
            model: Model name for logging
            **client_kwargs: Additional arguments passed to httpx.AsyncClient
        """
        self.logger = logger
        self.provider = provider
        self.model = model

        # Create event hooks for logging
        hooks = create_logging_hooks(logger, provider, model)

        # Merge with any existing event hooks
        existing_hooks = client_kwargs.get("event_hooks", {})
        for event, hook_list in hooks.items():
            if event in existing_hooks:
                existing_hooks[event].extend(hook_list)
            else:
                existing_hooks[event] = hook_list

        client_kwargs["event_hooks"] = existing_hooks

        # Create the underlying client with logging hooks
        self.client = httpx.AsyncClient(**client_kwargs)

    # Delegate all attributes to the wrapped client
    def __getattr__(self, name: str) -> Any:
        return getattr(self.client, name)

    async def __aenter__(self) -> "LoggingAsyncClient":
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.client.__aexit__(*args)
