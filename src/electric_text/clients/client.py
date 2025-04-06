import importlib
import json
from typing import AsyncGenerator, Any, Optional, Union  # , Generic
from electric_text.providers import ModelProvider  # , ResponseType

# from electric_text.clients.parse_partial_response import parse_partial_response
from pydantic import ValidationError
from dataclasses import dataclass


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


class Client:  # class Client(Generic[ResponseType])
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
        # response_model: type[ResponseType],
    ) -> AsyncGenerator[
        PromptResult, None
    ]:  # AsyncGenerator[ParseResult[ResponseType], None]:
        async for history in self.provider.generate_stream(messages, model):
            content = history.get_full_content()
            yield PromptResult(raw_content=content)
            # try:
            #     parsed_content = parse_partial_response(content)
            #     try:
            #         model_instance = response_model(**parsed_content)
            #         yield ParseResult(
            #             raw_content=content,
            #             parsed_content=parsed_content,
            #             model=model_instance,
            #         )
            #     except (ValidationError, TypeError) as error:
            #         yield ParseResult(
            #             raw_content=content,
            #             parsed_content=parsed_content,
            #             validation_error=error,
            #         )
            # except json.JSONDecodeError as error:
            #     yield ParseResult(
            #         raw_content=content,
            #         parsed_content={},
            #         json_error=error,
            #     )

    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        # response_model: type[ResponseType],
    ) -> PromptResult:  # ParseResult[ResponseType]:
        """
        Generate a complete response and return it wrapped in a ParseResult.

        Args:
            model: The model to use for generation
            messages: The messages to generate from
            # response_model: The type to parse the response into

        Returns:
            ParseResult containing the raw content, parsed content, and model instance if valid
        """
        history = await self.provider.generate_completion(messages, model)
        content = history.get_full_content()
        return PromptResult(raw_content=content)
        # try:
        #     parsed_content = parse_partial_response(content)
        #     try:
        #         model_instance = response_model(**parsed_content)
        #         return ParseResult(
        #             raw_content=content,
        #             parsed_content=parsed_content,
        #             model=model_instance,
        #         )
        #     except (ValidationError, TypeError) as error:
        #         return ParseResult(
        #             raw_content=content,
        #             parsed_content=parsed_content,
        #             validation_error=error,
        #         )
        # except json.JSONDecodeError as error:
        #     return ParseResult(
        #         raw_content=content,
        #         parsed_content={},
        #         json_error=error,
        #     )
