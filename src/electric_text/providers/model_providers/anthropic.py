import json
import httpx
from contextlib import asynccontextmanager
from typing import Any, Dict, Type, Optional, AsyncGenerator

from electric_text.providers import ModelProvider, ResponseType
from electric_text.providers.stream_history import (
    StreamChunk,
    StreamHistory,
    StreamChunkType,
)


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Error raised when response format is invalid."""

    pass


class AnthropicProvider(ModelProvider[ResponseType]):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com/v1/messages",
        default_model: str = "claude-3-sonnet-20240229",
        api_version: str = "2023-06-01",
        timeout: float = 30.0,
        **kwargs: Any,
    ):
        """
        Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key
            base_url: Base URL for the Anthropic API
            default_model: Default model to use for queries
            api_version: Anthropic API version
            timeout: Timeout for API requests in seconds
            **kwargs: Additional provider-specific options
        """
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.api_version = api_version
        self.format_schemas: Dict[Type[Any], Dict[str, Any]] = {}
        self.stream_history = StreamHistory()
        self.client_kwargs = {
            "timeout": timeout,
            "headers": {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": api_version,
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

        # Replace "system" with "user" in the messages.
        # NOTE: See convert_to_llm_messages() which is NOT provider specific.
        # Anthropic disallows "system" messages.
        messages = [
            {"role": "user", "content": message["content"]} for message in messages
        ]

        # Now, insert an assistant reply between the user messages.
        # Anthropic requires strict user/assistant/user... structure.
        messages.insert(
            1,
            {
                "role": "assistant",
                "content": "Acknowledged. I will respond with JSON.",
            },
        )

        return {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
            "max_tokens": 4096,  # Can be made configurable
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
        Stream responses from Anthropic.

        Args:
            messages: The list of messages to send
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional query-specific parameters

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        payload = self.create_payload(messages, response_type, model, stream=True)
        self.stream_history = StreamHistory()  # Reset stream history

        try:
            async with self.get_client() as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue

                        # Anthropic format: "event: <event_type>\ndata: <json_data>\n\n"
                        if line.startswith("data:"):
                            data_str = line[5:].strip()

                            try:
                                data = json.loads(data_str)

                                if "delta" in data and "text" in data["delta"]:
                                    content = data["delta"]["text"]
                                    stream_chunk = StreamChunk(
                                        type=StreamChunkType.CONTENT_CHUNK,
                                        raw_line=line,
                                        parsed_data=data,
                                        content=content,
                                    )
                                    self.stream_history.add_chunk(stream_chunk)
                                    yield self.stream_history
                                elif "type" in data and data["type"] == "message_stop":
                                    # Final message indicating completion
                                    stream_chunk = StreamChunk(
                                        type=StreamChunkType.COMPLETION_END,
                                        raw_line=line,
                                        parsed_data=data,
                                        content="",
                                    )
                                    self.stream_history.add_chunk(stream_chunk)
                                    yield self.stream_history
                                elif "error" in data:
                                    # Handle API errors
                                    error_chunk = StreamChunk(
                                        type=StreamChunkType.FORMAT_ERROR,
                                        raw_line=line,
                                        error=data["error"]["message"],
                                    )
                                    self.stream_history.add_chunk(error_chunk)
                                    yield self.stream_history

                            except json.JSONDecodeError as e:
                                error_chunk = StreamChunk(
                                    type=StreamChunkType.PARSE_ERROR,
                                    raw_line=line,
                                    error=str(e),
                                )
                                self.stream_history.add_chunk(error_chunk)
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
        Get a complete response from Anthropic.

        Args:
            messages: The list of messages to send
            response_type: Expected response type
            model: Optional model override
            **kwargs: Additional query-specific parameters

        Returns:
            StreamHistory containing the complete response
        """

        payload = self.create_payload(messages, response_type, model, stream=False)
        history = StreamHistory()

        try:
            async with self.get_client() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()

                try:
                    data = response.json()
                    # The content in Anthropic's response is in the content field of the message
                    raw_content = data["content"][0]["text"]

                    chunk = StreamChunk(
                        type=StreamChunkType.COMPLETE_RESPONSE,
                        raw_line=json.dumps(data),
                        parsed_data=data,
                        content=raw_content,
                    )

                    history.add_chunk(chunk)
                    return history

                except (KeyError, json.JSONDecodeError) as e:
                    error_chunk = StreamChunk(
                        type=StreamChunkType.FORMAT_ERROR,
                        raw_line=response.text,
                        error=f"Failed to parse response: {e}",
                    )
                    history.add_chunk(error_chunk)
                    return history
                except TypeError as e:
                    error_chunk = StreamChunk(
                        type=StreamChunkType.FORMAT_ERROR,
                        raw_line=response.text,
                        error=f"Response doesn't match expected type: {e}",
                    )
                    history.add_chunk(error_chunk)
                    return history

        except httpx.HTTPError as e:
            error_chunk = StreamChunk(
                type=StreamChunkType.HTTP_ERROR,
                raw_line="",
                error=f"Complete request failed: {e}",
            )
            history.add_chunk(error_chunk)
            return history
