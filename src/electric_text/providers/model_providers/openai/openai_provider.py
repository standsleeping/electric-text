import json
import httpx
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, AsyncGenerator
import logging

from electric_text.providers import ModelProvider
from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.openai.openai_provider_inputs import (
    OpenAIProviderInputs,
)
from electric_text.providers.model_providers.openai.convert_inputs import (
    convert_provider_inputs,
)
from electric_text.providers.data.stream_history import (
    StreamHistory,
)
from electric_text.providers.functions.categorize_stream_line import (
    categorize_stream_line,
)
from electric_text.providers.model_providers.openai.functions.set_text_format import (
    set_text_format,
)
from electric_text.providers.model_providers.openai.data.openai_response import (
    OpenAIResponse,
)


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class OpenaiProvider(ModelProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1/responses",
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
        format_schema: Optional[Dict[str, Any]] = None,
        strict_schema: bool = True,
    ) -> Dict[str, Any]:
        """
        Create the API request payload.

        Args:
            messages: The list of messages to send
            model: Model override (optional)
            stream: Whether to stream the response
            format_schema: Optional JSON schema for structured outputs
            strict_schema: Whether to enforce strict schema validation (default: True)

        Returns:
            Dict containing the formatted payload
        """
        payload = {
            "model": model or self.default_model,
            "input": messages,
            "stream": stream,
        }

        if format_schema:
            payload["text"] = set_text_format(format_schema, strict=strict_schema)

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
        request: ProviderRequest,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from OpenAI.

        Args:
            request: The request for the provider

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        self.stream_history = StreamHistory()  # Reset stream history

        # Convert the request to OpenAI inputs
        openai_inputs: OpenAIProviderInputs = convert_provider_inputs(request)

        messages = openai_inputs.messages
        model = openai_inputs.model
        format_schema = openai_inputs.format_schema
        strict_schema = getattr(openai_inputs, "strict_schema", True)

        payload = self.create_payload(
            messages=messages,
            model=model,
            stream=True,
            format_schema=format_schema,
            strict_schema=strict_schema,
        )

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
        request: ProviderRequest,
    ) -> StreamHistory:
        """
        Get a complete response from OpenAI.

        Args:
            request: The request for the provider

        Returns:
            StreamHistory containing the complete response
        """
        history = StreamHistory()

        # Convert the request to OpenAI inputs
        openai_inputs: OpenAIProviderInputs = convert_provider_inputs(request)

        messages = openai_inputs.messages
        model = openai_inputs.model
        format_schema = openai_inputs.format_schema
        strict_schema = getattr(openai_inputs, "strict_schema", True)

        payload = self.create_payload(
            messages=messages,
            model=model,
            stream=False,
            format_schema=format_schema,
            strict_schema=strict_schema,
        )

        # Debug log the payload to inspect schema structure
        if format_schema:
            log_line = f"Open AI schema: {json.dumps(payload.get('text', {}), indent=2)}"
            logging.debug(log_line)

        try:
            async with self.get_client() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()

                try:
                    data = response.json()
                    openai_response = OpenAIResponse.from_dict(data)

                    # Get the content text from the response
                    raw_content = openai_response.get_content_text()

                    if raw_content is None:
                        error_chunk = StreamChunk(
                            type=StreamChunkType.FORMAT_ERROR,
                            raw_line=response.text,
                            error="No content found in response",
                        )
                        history.add_chunk(error_chunk)
                        return history

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
