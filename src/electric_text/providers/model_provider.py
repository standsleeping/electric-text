from typing import (
    AsyncGenerator,
    Protocol,
    runtime_checkable,
)

from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.user_request import UserRequest


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol defining the interface that providers will implement."""

    stream_history: StreamHistory

    def generate_stream(
        self,
        request: UserRequest,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from the provider.

        Args:
            request: The request for the provider

        Yields:
            A generator of StreamHistory objects containing the full stream history after each chunk
        """
        ...

    async def generate_completion(
        self,
        request: UserRequest,
    ) -> StreamHistory:
        """
        Get a complete response from the provider.

        Args:
            request: The request for the provider

        Returns:
            A StreamHistory object containing the complete response
        """
        ...
