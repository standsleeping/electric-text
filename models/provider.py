from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Protocol,
    AsyncGenerator,
    runtime_checkable,
)

from models.stream_history import StreamHistory


@runtime_checkable
class JSONResponse(Protocol):
    """Protocol defining the required structure for response objects."""

    def __init__(self, **kwargs: Any) -> None: ...


# Type variable for response type, bounded by JSONResponse
ResponseType = TypeVar("ResponseType", bound="JSONResponse", contravariant=True)


@runtime_checkable
class ModelProvider(Protocol[ResponseType]):
    """Protocol defining the interface that providers will implement."""

    stream_history: StreamHistory

    def register_schema(
        self, response_type: Type[ResponseType], schema: Dict[str, Any]
    ) -> None:
        """
        Register a JSON schema for a response type.

        Args:
            response_type: The type to register a schema for
            schema: JSON schema defining the expected format
        """
        ...

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        response_type: Type[ResponseType],
        model: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from the provider.

        Args:
            messages: The list of messages
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional provider-specific parameters

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        ...

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        response_type: Type[ResponseType],
        model: str | None = None,
        **kwargs: Any,
    ) -> StreamHistory:
        """
        Get a complete response from the provider.

        Args:
            messages: The list of messages
            response_type: Expected response type (used for validation)
            model: Optional model override
            **kwargs: Additional provider-specific parameters

        Returns:
            StreamHistory containing the complete response
        """
        ...
