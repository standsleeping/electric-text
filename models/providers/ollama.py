import json
import httpx
from contextlib import asynccontextmanager
from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Protocol,
    Optional,
    AsyncGenerator,
    runtime_checkable,
)


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Raised when response format doesn't match expected schema."""

    pass


class APIError(ModelProviderError):
    """Raised when the API request fails."""

    pass


@runtime_checkable
class JSONResponse(Protocol):
    """Protocol defining the required structure for response objects."""

    def __init__(self, **kwargs: Any) -> None: ...


# Type variable for response type, bounded by JSONResponse
T = TypeVar("T", bound="JSONResponse")


@runtime_checkable
class ModelProvider(Protocol[T]):
    """Protocol defining the interface that providers will implement."""

    def query_stream(
        self,
        prompt: str,
        response_type: Type[T],
        model: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream responses from the provider.

        Args:
            prompt: The input prompt
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional provider-specific parameters

        Yields:
            Response chunks in the provider's format
        """
        ...

    async def query_complete(
        self,
        prompt: str,
        response_type: Type[T],
        model: str | None = None,
        **kwargs: Any,
    ) -> T:
        """
        Get a complete response from the provider.

        Args:
            prompt: The input prompt
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional provider-specific parameters

        Returns:
            Complete response in the specified type
        """
        ...


class OllamaProvider(ModelProvider[T]):
    def __init__(
        self,
        base_url: str = "http://localhost:11434/api/chat",
        default_model: str = "llama3.1:8b",
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        """
        Initialize the Ollama provider.

        Args:
            base_url: Base URL for the Ollama API
            default_model: Default model to use for queries
            timeout: Timeout for API requests in seconds
            **kwargs: Additional provider-specific options
        """
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.format_schemas: Dict[Type[Any], Dict[str, Any]] = {}
        self.client_kwargs = {
            "timeout": timeout,
            "headers": {"Content-Type": "application/json"},
            **kwargs,
        }

    def register_schema(self, response_type: Type[T], schema: Dict[str, Any]) -> None:
        """
        Register a JSON schema for a response type.

        Args:
            response_type: The type to register a schema for
            schema: JSON schema defining the expected format
        """
        self.format_schemas[response_type] = schema

    def create_payload(
        self, prompt: str, response_type: Type[T], model: Optional[str], stream: bool
    ) -> Dict[str, Any]:
        """
        Create the API request payload.

        Args:
            prompt: The prompt to send
            response_type: Expected response type
            model: Model override (optional)
            stream: Whether to stream the response

        Returns:
            Dict containing the formatted payload

        Raises:
            FormatError: If no schema is registered for the response type
        """
        if response_type not in self.format_schemas:
            raise FormatError(f"No schema registered for type {response_type.__name__}")

        return {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
            "format": self.format_schemas[response_type],
        }

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for httpx client."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            yield client

    async def query_stream(
        self,
        prompt: str,
        response_type: Type[T],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream responses from Ollama.

        Args:
            prompt: The input prompt
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional query-specific parameters

        Yields:
            Response chunks in Ollama's format

        Raises:
            APIError: If the API request fails
            FormatError: If response parsing fails
        """
        payload = self.create_payload(prompt, response_type, model, stream=True)

        try:
            async with self.get_client() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}",
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            chunk = json.loads(line)
                            yield chunk
                        except json.JSONDecodeError as e:
                            raise FormatError(f"Failed to parse chunk: {e}")

        except httpx.HTTPError as e:
            raise APIError(f"Stream request failed: {e}")

    async def query_complete(
        self,
        prompt: str,
        response_type: Type[T],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """
        Get a complete response from Ollama.

        Args:
            prompt: The input prompt
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional query-specific parameters

        Returns:
            Complete response in the specified type

        Raises:
            APIError: If the API request fails
            FormatError: If response parsing fails
        """
        payload = self.create_payload(prompt, response_type, model, stream=False)

        try:
            async with self.get_client() as client:
                response = await client.post(f"{self.base_url}", json=payload)
                response.raise_for_status()

                try:
                    data = response.json()
                    content = json.loads(data["message"]["content"])
                    return response_type(**content)

                except (KeyError, json.JSONDecodeError) as e:
                    raise FormatError(f"Failed to parse response: {e}")
                except TypeError as e:
                    raise FormatError(f"Response doesn't match expected type: {e}")

        except httpx.HTTPError as e:
            raise APIError(f"Complete request failed: {e}")
