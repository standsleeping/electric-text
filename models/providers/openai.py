import json
import httpx
from contextlib import asynccontextmanager
from typing import Any, Dict, Type, Optional, AsyncGenerator

from models.provider import ModelProvider, ResponseType
from models.stream_history import (
    StreamChunk,
    StreamHistory,
    StreamChunkType,
    categorize_stream_line,
)


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Raised when response format doesn't match expected schema."""

    pass


class OpenaiProvider(ModelProvider[ResponseType]):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1/chat/completions",
        default_model: str = "gpt-4o-mini",
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
            base_url: Base URL for the OpenAI API
            default_model: Default model to use for queries
            timeout: Timeout for API requests in seconds
            **kwargs: Additional provider-specific options
        """
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.format_schemas: Dict[Type[Any], Dict[str, Any]] = {}
        self.stream_history = StreamHistory()
        self.client_kwargs = {
            "timeout": timeout,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            **kwargs,
        }

    def register_schema(
        self, response_type: Type[ResponseType], schema: Dict[str, Any]
    ) -> None:
        """
        Register a JSON schema for a response type.

        Args:
            response_type: The type to register a schema for
            schema: JSON schema defining the expected format
        """
        self.format_schemas[response_type] = schema

    def create_payload(
        self,
        messages: list[dict[str, str]],
        response_type: Type[ResponseType],
        model: Optional[str],
        stream: bool,
    ) -> Dict[str, Any]:
        """
        Create the API request payload.

        Args:
            messages: The list of messages to send
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

        # Add system message to enforce JSON schema
        schema_message = {
            "role": "system",
            "content": f"Respond with JSON matching this schema: {json.dumps(self.format_schemas[response_type])}",
        }

        return {
            "model": model or self.default_model,
            "messages": [schema_message] + messages,
            "stream": stream,
            "response_format": {"type": "json_object"},
        }

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for httpx client."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            yield client

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        response_type: Type[ResponseType],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from OpenAI.

        Args:
            messages: The list of messages to send
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional query-specific parameters

        Yields:
            StreamHistory object containing the full stream history after each chunk

        Raises:
            FormatError: If response parsing fails
        """
        payload = self.create_payload(messages, response_type, model, stream=True)

        try:
            async with self.get_client() as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        chunk = categorize_stream_line(line)
                        self.stream_history.add_chunk(chunk)
                        yield self.stream_history

        except httpx.HTTPError as e:
            error_chunk = StreamChunk(
                type=StreamChunkType.HTTP_ERROR,
                raw_line="",
                error=f"Stream request failed: {e}",
            )
            self.stream_history.add_chunk(error_chunk)
            yield self.stream_history

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        response_type: Type[ResponseType],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> StreamHistory:
        """
        Get a complete response from OpenAI.

        Args:
            messages: The list of messages to send
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional query-specific parameters

        Returns:
            StreamHistory containing the complete response

        Raises:
            FormatError: If response parsing fails
        """
        payload = self.create_payload(messages, response_type, model, stream=False)
        history = StreamHistory()

        try:
            async with self.get_client() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()

                try:
                    data = response.json()
                    raw_content = data["choices"][0]["message"]["content"]

                    chunk = StreamChunk(
                        type=StreamChunkType.COMPLETE_RESPONSE,
                        raw_line=json.dumps(data),
                        parsed_data=data,
                        content=raw_content,
                    )

                    history.add_chunk(chunk)
                    return history

                except (KeyError, json.JSONDecodeError) as e:
                    raise FormatError(f"Failed to parse response: {e}")
                except TypeError as e:
                    raise FormatError(f"Response doesn't match expected type: {e}")

        except httpx.HTTPError as e:
            error_chunk = StreamChunk(
                type=StreamChunkType.HTTP_ERROR,
                raw_line="",
                error=f"Complete request failed: {e}",
            )
            history.add_chunk(error_chunk)
            return history
