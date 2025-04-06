import json
import httpx
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, AsyncGenerator

from electric_text.providers import ModelProvider
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


class OllamaProvider(ModelProvider):
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
        self.stream_history = StreamHistory()
        self.client_kwargs = {
            "timeout": timeout,
            "headers": {"Content-Type": "application/json"},
            **kwargs,
        }

    def create_payload(
        self,
        messages: list[dict[str, str]],
        model: Optional[str],
        stream: bool,
        format_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create the API request payload.

        Args:
            messages: The list of messages to send
            model: Model override (optional)
            stream: Whether to stream the response
            format_schema: Optional JSON schema for structured output

        Returns:
            Dict containing the formatted payload
        """
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
        }
        
        # Add format if schema is provided
        if format_schema is not None:
            payload["format"] = format_schema
            
        return payload

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for httpx client."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            yield client

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        *,
        format_schema: Optional[Dict[str, Any]] = None,
        prefill_content: str | None = None,
        structured_prefill: bool = False,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from Ollama.

        Args:
            messages: The list of messages to send
            model: Optional model override
            format_schema: Optional JSON schema for structured output
            prefill_content: Ignored, Ollama doesn't support prefilling
            structured_prefill: Ignored, Ollama doesn't support prefilling
            **kwargs: Additional provider-specific parameters

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        self.stream_history = StreamHistory()  # Reset stream history

        # Create the payload
        payload = self.create_payload(messages, model, stream=True, format_schema=format_schema)

        try:
            async with self.get_client() as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            chunk = json.loads(line)
                            stream_chunk = StreamChunk(
                                type=StreamChunkType.CONTENT_CHUNK,
                                raw_line=line,
                                parsed_data=chunk,
                                content=chunk.get("message", {}).get("content"),
                            )
                            self.stream_history.add_chunk(stream_chunk)
                            yield self.stream_history

                            # Check for done flag
                            if chunk.get("done", False):
                                # Final message indicating completion
                                stream_chunk = StreamChunk(
                                    type=StreamChunkType.COMPLETION_END,
                                    raw_line=line,
                                    parsed_data=chunk,
                                    content="",
                                )
                                self.stream_history.add_chunk(stream_chunk)
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
        model: Optional[str] = None,
        *,
        format_schema: Optional[Dict[str, Any]] = None,
        prefill_content: str | None = None,
        structured_prefill: bool = False,
        **kwargs: Any,
    ) -> StreamHistory:
        """
        Get a complete response from Ollama.

        Args:
            messages: The list of messages to send
            model: Optional model override
            format_schema: Optional JSON schema for structured output
            prefill_content: Ignored, Ollama doesn't support prefilling
            structured_prefill: Ignored, Ollama doesn't support prefilling
            **kwargs: Additional provider-specific parameters

        Returns:
            StreamHistory containing the complete response
        """
        history = StreamHistory()

        payload = self.create_payload(messages, model, stream=False, format_schema=format_schema)

        try:
            async with self.get_client() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()

                try:
                    data = response.json()
                    # The content in Ollama's response is in the content field of the message
                    raw_content = data["message"]["content"]

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
