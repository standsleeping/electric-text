import json
import httpx
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional
import logging

from electric_text.providers import ModelProvider
from electric_text.providers.logging import HttpLogger, LoggingAsyncClient
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
from electric_text.providers.model_providers.openai.functions.process_stream_response import (
    process_stream_response,
)
from electric_text.providers.model_providers.openai.functions.set_text_format import (
    set_text_format,
)
from electric_text.providers.model_providers.openai.functions.process_completion_response import (
    process_completion_response,
)
from electric_text.providers.model_providers.openai.functions.create_payload import (
    create_payload,
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

        # Initialize HTTP logger if enabled via environment variable
        self.http_logger: Optional[HttpLogger] = None
        if os.getenv("ELECTRIC_TEXT_HTTP_LOGGING", "false").lower() == "true":
            from pathlib import Path

            log_dir = Path(os.getenv("ELECTRIC_TEXT_HTTP_LOG_DIR", "./http_logs"))
            self.http_logger = HttpLogger(log_dir=log_dir, enabled=True)

    @asynccontextmanager
    async def get_client(
        self,
    ) -> AsyncGenerator[httpx.AsyncClient | LoggingAsyncClient, None]:
        """Context manager for httpx client."""
        if self.http_logger:
            # Create a logging client with the same kwargs
            async with LoggingAsyncClient(
                logger=self.http_logger, provider="openai", **self.client_kwargs
            ) as client:
                yield client
        else:
            async with httpx.AsyncClient(**self.client_kwargs) as client:
                yield client

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
        tools = openai_inputs.tools

        payload = create_payload(
            model,
            self.default_model,
            messages,
            stream=True,
            format_schema=format_schema,
            strict_schema=strict_schema,
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
        Get a complete response from OpenAI.

        Args:
            request: The request for the provider

        Returns:
            StreamHistory containing the complete response
        """
        self.stream_history = StreamHistory()

        # Convert the request to OpenAI inputs
        openai_inputs: OpenAIProviderInputs = convert_provider_inputs(request)

        messages = openai_inputs.messages
        model = openai_inputs.model
        format_schema = openai_inputs.format_schema
        strict_schema = getattr(openai_inputs, "strict_schema", True)
        tools = openai_inputs.tools

        payload = create_payload(
            model,
            self.default_model,
            messages,
            stream=False,
            format_schema=format_schema,
            strict_schema=strict_schema,
            tools=tools,
        )

        # Debug log the payload to inspect schema structure
        if format_schema:
            log_line = f"OAI schema: {json.dumps(payload.get('text', {}), indent=2)}"
            logging.debug(log_line)

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
