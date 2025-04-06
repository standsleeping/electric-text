import json
import httpx
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, AsyncGenerator

from electric_text.providers import ModelProvider
from electric_text.providers.stream_history import (
    StreamChunk,
    StreamHistory,
    StreamChunkType,
    categorize_stream_line,
)


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Error raised when response format is invalid."""

    pass


class OpenaiProvider(ModelProvider):
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
        self.stream_history = StreamHistory()
        self.client_kwargs = {
            "timeout": timeout,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            **kwargs,
        }

    def create_payload(
        self,
        messages: list[dict[str, str]],
        model: Optional[str],
        stream: bool,
    ) -> Dict[str, Any]:
        """
        Create the API request payload.

        Args:
            messages: The list of messages to send
            model: Model override (optional)
            stream: Whether to stream the response

        Returns:
            Dict containing the formatted payload
        """
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
        }

        return payload

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for httpx client."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            yield client

    async def stream_response(
        self, client: httpx.AsyncClient, url: str, payload: Dict[str, Any]
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Helper method to stream response chunks.

        Args:
            client: The HTTP client
            url: The URL to stream from
            payload: The request payload

        Yields:
            StreamChunk objects parsed from the response
        """
        async with client.stream(
            "POST",
            url,
            json=payload,
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                yield categorize_stream_line(line)

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        *,
        prefill_content: str | None = None,
        structured_prefill: bool = False,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from OpenAI.

        Args:
            messages: The list of messages to send
            model: Optional model override
            prefill_content: Ignored, OpenAI doesn't support prefilling
            structured_prefill: Ignored, OpenAI doesn't support prefilling
            **kwargs: Additional provider-specific parameters

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        self.stream_history = StreamHistory()  # Reset stream history

        payload = self.create_payload(messages, model, stream=True)

        try:
            async with self.get_client() as client:
                async for chunk in self.stream_response(client, self.base_url, payload):
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
        model: Optional[str] = None,
        *,
        prefill_content: str | None = None,
        structured_prefill: bool = False,
        **kwargs: Any,
    ) -> StreamHistory:
        """
        Get a complete response from OpenAI.

        Args:
            messages: The list of messages to send
            model: Optional model override
            prefill_content: Ignored, OpenAI doesn't support prefilling
            structured_prefill: Ignored, OpenAI doesn't support prefilling
            **kwargs: Additional provider-specific parameters

        Returns:
            StreamHistory containing the complete response
        """
        history = StreamHistory()

        payload = self.create_payload(messages, model, stream=False)

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
