import httpx
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from electric_text.providers import ModelProvider
from electric_text.providers.logging import HttpLogger, LoggingAsyncClient
from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.anthropic.data.anthropic_provider_inputs import (
    AnthropicProviderInputs,
)
from electric_text.providers.model_providers.anthropic.functions.convert_inputs import (
    convert_provider_inputs,
)
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.anthropic.functions.process_stream_response import (
    process_stream_response,
)
from electric_text.providers.model_providers.anthropic.functions.process_completion_response import (
    process_completion_response,
)
from electric_text.providers.model_providers.anthropic.functions.create_payload import (
    create_payload,
)


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Error raised when response format is invalid."""

    pass


class AnthropicProvider(ModelProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com/v1/messages",
        default_model: str = "claude-3-sonnet-20240229",
        api_version: str = "2023-06-01",
        timeout: float = 30.0,
        http_logging_enabled: bool = False,
        http_log_dir: str = "./http_logs",
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

        # Initialize HTTP logger if enabled
        self.http_logger: Optional[HttpLogger] = None
        if http_logging_enabled:
            from pathlib import Path
            self.http_logger = HttpLogger(log_dir=Path(http_log_dir), enabled=True)

    def prefill_content(self) -> str:
        """
        Provide a standard prefill content for all response types.

        Returns:
            str: The prefill content to use
        """
        # Currently we only use "{" for all response types, but this could be
        # customized per response type in the future if needed
        return "{"

    def transform_messages(
        self, messages: list[dict[str, str]], prefill_content: str | None = None
    ) -> list[dict[str, str]]:
        """
        Transform the messages to the format required by the Anthropic API.
        """
        # Anthropic disallows "system" messages.
        # Replace each "system" message with a user message containing the system content,
        # followed by an assistant message that says "Acknowledged."
        transformed_messages = []
        for message in messages:
            if message.get("role") == "system":
                transformed_messages.append(
                    {"role": "user", "content": message["content"]}
                )
                transformed_messages.append(
                    {"role": "assistant", "content": "Acknowledged."}
                )
            else:
                transformed_messages.append(message)

        # Now, prefill Claude's response as the final message.
        # (https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response)
        if prefill_content:
            transformed_messages.append(
                {
                    "role": "assistant",
                    "content": prefill_content,
                },
            )

        return transformed_messages

    @asynccontextmanager
    async def get_client(
        self,
    ) -> AsyncGenerator[httpx.AsyncClient | LoggingAsyncClient, None]:
        """Context manager for httpx client."""
        if self.http_logger:
            # Create a logging client with the same kwargs
            async with LoggingAsyncClient(
                logger=self.http_logger, provider="anthropic", **self.client_kwargs
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
        Stream responses from Anthropic.

        Args:
            inputs: The inputs for the provider

        Yields:
            A generator of StreamHistory objects containing the full stream history after each chunk
        """
        self.stream_history = StreamHistory()

        anthropic_inputs: AnthropicProviderInputs = convert_provider_inputs(request)

        messages = anthropic_inputs.messages
        model = anthropic_inputs.model
        structured_prefill = anthropic_inputs.structured_prefill

        prefill = None
        if structured_prefill:
            prefill = self.prefill_content()

            prefill_chunk = StreamChunk(
                type=StreamChunkType.PREFILLED_CONTENT,
                raw_line="",
                parsed_data=None,
            )

            self.stream_history.add_chunk(prefill_chunk)

        final_messages = self.transform_messages(messages, prefill)
        tools = anthropic_inputs.tools

        payload = create_payload(
            model=model,
            default_model=self.default_model,
            messages=final_messages,
            stream=True,
            max_tokens=anthropic_inputs.max_tokens,
            tools=tools,
        )

        yield self.stream_history  # Yield immediately so consumer gets the prefill

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
        Get a complete response from Anthropic.

        Args:
            request: The request for the provider

        Returns:
            StreamHistory containing the complete response
        """
        self.stream_history = StreamHistory()

        anthropic_inputs: AnthropicProviderInputs = convert_provider_inputs(request)

        messages = anthropic_inputs.messages
        model = anthropic_inputs.model
        structured_prefill = anthropic_inputs.structured_prefill

        prefill = None
        if structured_prefill:
            prefill = self.prefill_content()
            prefill_chunk = StreamChunk(
                type=StreamChunkType.PREFILLED_CONTENT,
                raw_line="",
                parsed_data=None,
            )

            self.stream_history.add_chunk(prefill_chunk)

        final_messages = self.transform_messages(messages, prefill)
        tools = anthropic_inputs.tools

        payload = create_payload(
            model=model,
            default_model=self.default_model,
            messages=final_messages,
            stream=False,
            max_tokens=anthropic_inputs.max_tokens,
            tools=tools,
        )

        try:
            async with self.get_client() as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                line: str = response.text
                return process_completion_response(line, self.stream_history)
        except httpx.HTTPError as e:
            return self.stream_history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.HTTP_ERROR,
                    raw_line="",
                    error=f"Complete request failed: {e}",
                )
            )
