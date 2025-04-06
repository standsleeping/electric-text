from typing import (
    Any,
    AsyncGenerator,
    Protocol,
    runtime_checkable,
)

from electric_text.providers.stream_history import StreamHistory


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol defining the interface that providers will implement."""

    stream_history: StreamHistory

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from the provider.

        Args:
            messages: The list of messages
            model: Optional model override
            **kwargs: Additional provider-specific parameters

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        ...

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> StreamHistory:
        """
        Get a complete response from the provider.

        Args:
            messages: The list of messages
            model: Optional model override
            **kwargs: Additional provider-specific parameters

        Returns:
            StreamHistory containing the complete response
        """
        ...
