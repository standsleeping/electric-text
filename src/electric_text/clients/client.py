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
    Dict,
    Type,
)

from electric_text.providers import ModelProvider
from electric_text.clients.parse_partial_response import parse_partial_response
from electric_text.clients.transformers import prepare_provider_request


@runtime_checkable
class JSONResponse(Protocol):
    """Protocol defining the required structure for response objects."""

    def __init__(self, **kwargs: Any) -> None: ...

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]: ...


# Type variable for response type, bounded by JSONResponse
ResponseType = TypeVar("ResponseType", bound="JSONResponse", contravariant=True)
T = TypeVar("T", bound=JSONResponse)


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
    provider_name: str

    def __init__(self, provider_name: str, config: dict[str, str] = {}) -> None:
        self.provider_name = provider_name
        provider_module = f"electric_text.providers.model_providers.{provider_name}"
        module = importlib.import_module(provider_module)
        provider_class = getattr(module, f"{provider_name.title()}Provider")
        self.provider = provider_class(**config)

    async def stream_raw(
        self,
        model: str,
        messages: list[dict[str, str]],
        prefill_content: Optional[str] = None,
    ) -> AsyncGenerator[PromptResult, None]:
        """
        Stream a raw response from the model without parsing.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            prefill_content: Optional content to prefill the model with

        Returns:
            AsyncGenerator[PromptResult, None]: A generator of PromptResult objects
        """
        # Prepare request with transformations
        base_request = {
            "messages": messages,
            "model": model,
        }

        # Transform request using functional transformers
        provider_request = prepare_provider_request(
            base_request,
            provider_name=self.provider_name,
            prefill_content=prefill_content,
        )

        # Extract parameters for generate_stream
        stream_kwargs = {
            k: v for k, v in provider_request.items() if k not in ["messages", "model"]
        }

        # Call provider with transformed request
        async for history in self.provider.generate_stream(
            messages, model, **stream_kwargs
        ):
            content = history.get_full_content()
            yield PromptResult(raw_content=content)

    async def generate_raw(
        self,
        model: str,
        messages: list[dict[str, str]],
        prefill_content: Optional[str] = None,
    ) -> PromptResult:
        """
        Generate a complete raw response without parsing.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            prefill_content: Optional content to prefill the model with

        Returns:
            PromptResult: Contains the raw content
        """
        # Prepare request with transformations
        base_request = {
            "messages": messages,
            "model": model,
        }

        # Transform request using functional transformers
        provider_request = prepare_provider_request(
            base_request,
            provider_name=self.provider_name,
            prefill_content=prefill_content,
        )

        # Extract parameters for generate_completion
        completion_kwargs = {
            k: v for k, v in provider_request.items() if k not in ["messages", "model"]
        }

        # Call provider with transformed request
        history = await self.provider.generate_completion(
            messages, model, **completion_kwargs
        )

        content = history.get_full_content()
        return PromptResult(raw_content=content)

    async def stream_structured(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
        prefill_content: Optional[str] = None,
    ) -> AsyncGenerator[ParseResult[ResponseType], None]:
        """
        Stream a response from the model and parse it into a structured object.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            response_model: The type to parse the response into
            prefill_content: Optional content to prefill the model with

        Returns:
            AsyncGenerator[ParseResult[ResponseType], None]: A generator of ParseResult objects
        """
        # Prepare base request with just the core parameters
        base_request = {
            "messages": messages,
            "model": model,
        }

        # Transform request using functional transformers
        provider_request = prepare_provider_request(
            base_request,
            response_model=response_model,
            provider_name=self.provider_name,
            prefill_content=prefill_content,
        )

        # Extract parameters for generate_stream
        stream_kwargs = {
            k: v for k, v in provider_request.items() if k not in ["messages", "model"]
        }

        # Call provider with transformed request
        async for history in self.provider.generate_stream(
            messages, model, **stream_kwargs
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

    async def generate_structured(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
        prefill_content: Optional[str] = None,
    ) -> ParseResult[ResponseType]:
        """
        Generate a complete response and parse it into a structured object.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            response_model: The type to parse the response into
            prefill_content: Optional content to prefill the model with

        Returns:
            ParseResult containing the raw content, parsed content, and model instance if valid
        """
        # Prepare base request with just the core parameters
        base_request = {
            "messages": messages,
            "model": model,
        }

        # Transform request using functional transformers
        provider_request = prepare_provider_request(
            base_request,
            response_model=response_model,
            provider_name=self.provider_name,
            prefill_content=prefill_content,
        )

        # Extract parameters for generate_completion
        completion_kwargs = {
            k: v for k, v in provider_request.items() if k not in ["messages", "model"]
        }

        # Call provider with transformed request
        history = await self.provider.generate_completion(
            messages, model, **completion_kwargs
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

    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        response_model: Optional[Type[T]] = None,
    ) -> Union[PromptResult, ParseResult[T]]:
        """
        Generate a complete response from the model.

        If response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be returned.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            response_model: Optional type to parse the response into

        Returns:
            PromptResult if no response_model is provided, otherwise ParseResult[T]
        """
        if response_model is not None:
            return await self.generate_structured(
                model, messages, response_model, prefill_content=None
            )
        return await self.generate_raw(model, messages, prefill_content=None)

    async def stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        response_model: Optional[Type[T]] = None,
    ) -> Union[
        AsyncGenerator[PromptResult, None], AsyncGenerator[ParseResult[T], None]
    ]:
        """
        Stream a response from the model.

        If response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be streamed.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            response_model: Optional type to parse the response into

        Returns:
            AsyncGenerator of PromptResult if no response_model is provided,
            otherwise AsyncGenerator of ParseResult[T]
        """
        if response_model is not None:
            return self.stream_structured(
                model, messages, response_model, prefill_content=None
            )
        return self.stream_raw(model, messages, prefill_content=None)
