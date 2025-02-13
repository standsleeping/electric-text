import importlib
import json
from typing import AsyncGenerator, Generic, Any, Optional, Union
from models.provider import ModelProvider, ResponseType
from models.parse_partial_response import parse_partial_response
from pydantic import ValidationError
from dataclasses import dataclass


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
        """Check if the parse result contains a valid model."""
        return self.model is not None


class Client(Generic[ResponseType]):
    provider: ModelProvider[ResponseType]

    def __init__(self, provider_name: str, config: dict[str, str] = {}) -> None:
        provider_module = f"models.providers.{provider_name}"
        module = importlib.import_module(provider_module, package="models")
        provider_class = getattr(module, f"{provider_name.title()}Provider")
        self.provider = provider_class(**config)

    async def stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
    ) -> AsyncGenerator[ParseResult[ResponseType], None]:
        async for history in self.provider.query_stream(
            messages, response_model, model
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

    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
    ) -> ResponseType:
        return await self.provider.query_complete(messages, response_model, model)
