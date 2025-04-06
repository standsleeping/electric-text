import json
import importlib
from dataclasses import dataclass
from pydantic import ValidationError
from typing import (
    AsyncGenerator,
    Any,
    Optional,
    Union,
    TypeVar,
    Protocol,
    runtime_checkable,
)

from electric_text.providers import ModelProvider
from electric_text.clients.parse_partial_response import parse_partial_response


@runtime_checkable
class JSONResponse(Protocol):
    """Protocol defining the required structure for response objects."""

    def __init__(self, **kwargs: Any) -> None: ...


# Type variable for response type, bounded by JSONResponse
ResponseType = TypeVar("ResponseType", bound="JSONResponse", contravariant=True)


@dataclass
class PromptResult:
    """Model response data."""

    raw_content: str


@dataclass
class ParseResult[T]:
    """Wrapper for parsed response data that may be incomplete."""

    raw_content: str
    parsed_content: dict[str, Any]
    model: Optional[T] = None
    validation_error: Optional[Union[ValidationError, TypeError]] = None
    json_error: Optional[json.JSONDecodeError] = None

    @property
    def is_valid(self) -> bool:
        """Checks for a valid model."""
        return self.model is not None


class Client:
    provider: ModelProvider

    def __init__(self, provider_name: str, config: dict[str, str] = {}) -> None:
        provider_module = f"electric_text.providers.model_providers.{provider_name}.{provider_name}_provider"
        module = importlib.import_module(provider_module, package="models")
        provider_class = getattr(module, f"{provider_name.title()}Provider")
        self.provider = provider_class(**config)

    async def stream(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> AsyncGenerator[PromptResult, None]:
        """
        Stream a response from the model.

        Args:
            model: The model to use for generation
            messages: The messages to generate from

        Returns:
            AsyncGenerator[PromptResult, None]: A generator of PromptResult objects
        """

        async for history in self.provider.generate_stream(messages, model):
            content = history.get_full_content()
            yield PromptResult(raw_content=content)

    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> PromptResult:
        """
        Generate a complete response and return it wrapped in a ParseResult.

        Args:
            model: The model to use for generation
            messages: The messages to generate from

        Returns:
            ParseResult containing the raw content, parsed content, and model instance if valid
        """
        history = await self.provider.generate_completion(messages, model)
        content = history.get_full_content()
        return PromptResult(raw_content=content)

    async def structured_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
    ) -> AsyncGenerator[ParseResult[ResponseType], None]:
        """
        Stream a response from the model and parse it into a structured object.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            response_model: The type to parse the response into

        Returns:
            AsyncGenerator[ParseResult[ResponseType], None]: A generator of ParseResult objects
        """
        async for history in self.provider.generate_stream(
            messages,
            model,
            structured_prefill=True,
        ):
            content = history.get_full_content()
            try:
                parsed_content = parse_partial_response(content)
                try:
                    model_instance = response_model(**parsed_content)
                    yield ParseResult(
                        raw_content=content,
                        parsed_content=parsed_content,
                        model=model_instance,
                    )
                except (ValidationError, TypeError) as error:
                    yield ParseResult(
                        raw_content=content,
                        parsed_content=parsed_content,
                        validation_error=error,
                    )
            except json.JSONDecodeError as error:
                yield ParseResult(
                    raw_content=content,
                    parsed_content={},
                    json_error=error,
                )

    async def structured_generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
    ) -> ParseResult[ResponseType]:
        """
        Generate a complete response and return it wrapped in a ParseResult.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            response_model: The type to parse the response into

        Returns:
            ParseResult containing the raw content, parsed content, and model instance if valid
        """
        history = await self.provider.generate_completion(
            messages,
            model,
            structured_prefill=True,
        )

        content = history.get_full_content()

        try:
            parsed_content = parse_partial_response(content)
            try:
                model_instance = response_model(**parsed_content)
                return ParseResult(
                    raw_content=content,
                    parsed_content=parsed_content,
                    model=model_instance,
                )
            except (ValidationError, TypeError) as error:
                return ParseResult(
                    raw_content=content,
                    parsed_content=parsed_content,
                    validation_error=error,
                )
        except json.JSONDecodeError as error:
            return ParseResult(
                raw_content=content,
                parsed_content={},
                json_error=error,
            )
