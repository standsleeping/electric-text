import httpx
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from electric_text.providers import ModelProvider
from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.ollama.functions.convert_inputs import (
    convert_provider_inputs,
)
from electric_text.providers.data.stream_history import (
    StreamHistory,
)
from electric_text.providers.model_providers.ollama.data.ollama_provider_inputs import (
    OllamaProviderInputs,
)
from electric_text.providers.model_providers.ollama.functions.process_completion_response import (
    process_completion_response,
)
from electric_text.providers.model_providers.ollama.functions.process_stream_response import (
    process_stream_response,
)
from electric_text.providers.model_providers.ollama.functions.create_payload import (
    create_payload,
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

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for httpx client."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            yield client

    async def generate_stream(
        self,
        request: ProviderRequest,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from Ollama.

        Args:
            request: The request for the provider

        Yields:
            StreamHistory object containing the full stream history after each chunk
        """
        self.stream_history = StreamHistory()  # Reset stream history

        ollama_inputs: OllamaProviderInputs = convert_provider_inputs(request)

        messages = ollama_inputs.messages
        model = ollama_inputs.model
        format_schema = ollama_inputs.format_schema
        tools = ollama_inputs.tools

        payload = create_payload(
            model,
            self.default_model,
            messages,
            stream=True,
            format_schema=format_schema,
            tools=tools,
        )

        try:
            async with self.get_client() as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        yield process_stream_response(line, self.stream_history)
        except httpx.HTTPError as e:
            yield self.stream_history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.HTTP_ERROR,
                    raw_line="",
                    error=f"Stream request failed: {e}",
                )
            )

    async def generate_completion(
        self,
        request: ProviderRequest,
    ) -> StreamHistory:
        """
        Get a complete response from Ollama.

        Args:
            request: The request for the provider

        Returns:
            StreamHistory containing the complete response
        """
        self.stream_history = StreamHistory()

        ollama_inputs: OllamaProviderInputs = convert_provider_inputs(request)

        messages = ollama_inputs.messages
        model = ollama_inputs.model
        format_schema = ollama_inputs.format_schema
        tools = ollama_inputs.tools

        payload = create_payload(
            model,
            self.default_model,
            messages,
            stream=False,
            format_schema=format_schema,
            tools=tools,
        )

        try:
            async with self.get_client() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                line = response.text
                return process_completion_response(line, self.stream_history)
        except httpx.HTTPError as e:
            return self.stream_history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.HTTP_ERROR,
                    raw_line="",
                    error=f"Complete request failed: {e}",
                )
            )
