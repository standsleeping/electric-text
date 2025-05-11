import json
import httpx
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, AsyncGenerator

from electric_text.providers import ModelProvider
from electric_text.providers.data.user_request import UserRequest
from electric_text.providers.model_providers.anthropic.anthropic_provider_inputs import (
    AnthropicProviderInputs,
)
from electric_text.providers.model_providers.anthropic.convert_inputs import (
    convert_user_request_to_provider_inputs,
)
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


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

    def create_payload(
        self,
        messages: list[dict[str, str]],
        model: Optional[str],
        stream: bool,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create the API request payload.

        Args:
            messages: The list of messages to send
            model: Model override (optional)
            stream: Whether to stream the response
            max_tokens: Maximum number of tokens to generate (optional)

        Returns:
            Dict containing the formatted payload
        """

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
        }

        # Use provided max_tokens or default to 4096
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        else:
            payload["max_tokens"] = 4096

        return payload

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for httpx client."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            yield client

    async def generate_stream(
        self,
        request: UserRequest,
    ) -> AsyncGenerator[StreamHistory, None]:
        """
        Stream responses from Anthropic.

        Args:
            inputs: The inputs for the provider

        Yields:
            A generator of StreamHistory objects containing the full stream history after each chunk
        """
        self.stream_history = StreamHistory()  # Reset stream history

        # From this point, inputs is treated as AnthropicProviderInputs
        anthropic_inputs: AnthropicProviderInputs = (
            convert_user_request_to_provider_inputs(request)
        )

        messages = anthropic_inputs.messages
        model = anthropic_inputs.model
        prefill_content = anthropic_inputs.prefill_content
        structured_prefill = anthropic_inputs.structured_prefill

        prefill = None
        if structured_prefill or prefill_content:
            prefill = self.prefill_content() if structured_prefill else prefill_content

            prefill_chunk = StreamChunk(
                type=StreamChunkType.PREFILLED_CONTENT,
                raw_line="",
                parsed_data=None,
                content=prefill,
            )

            self.stream_history.add_chunk(prefill_chunk)

        final_messages = self.transform_messages(messages, prefill)

        payload = self.create_payload(
            final_messages, model, stream=True, max_tokens=anthropic_inputs.max_tokens
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
                        else:
                            error_chunk = StreamChunk(
                                type=StreamChunkType.UNHANDLED_LINE,
                                raw_line=line,
                                error=f"Unhandled line: {line}",
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
        request: UserRequest,
    ) -> StreamHistory:
        """
        Get a complete response from Anthropic.

        Args:
            request: The request for the provider

        Returns:
            StreamHistory containing the complete response
        """
        history = StreamHistory()

        anthropic_inputs: AnthropicProviderInputs = (
            convert_user_request_to_provider_inputs(request)
        )

        messages = anthropic_inputs.messages
        model = anthropic_inputs.model
        prefill_content = anthropic_inputs.prefill_content
        structured_prefill = anthropic_inputs.structured_prefill

        prefill = None
        if structured_prefill or prefill_content:
            prefill = self.prefill_content() if structured_prefill else prefill_content
            prefill_chunk = StreamChunk(
                type=StreamChunkType.PREFILLED_CONTENT,
                raw_line="",
                parsed_data=None,
                content=prefill,
            )

            history.add_chunk(prefill_chunk)

        final_messages = self.transform_messages(messages, prefill)

        payload = self.create_payload(
            final_messages, model, stream=False, max_tokens=anthropic_inputs.max_tokens
        )

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
