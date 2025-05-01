import importlib
from typing import (
    AsyncGenerator,
    Union,
)

from electric_text.providers import ModelProvider
from electric_text.responses import UserRequest
from electric_text.clients.data import ParseResult, PromptResult, ResponseType, T
from electric_text.clients.functions.create_parse_result import create_parse_result


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
        request: UserRequest,
    ) -> AsyncGenerator[PromptResult, None]:
        """
        Stream a raw response from the model without parsing.

        Args:
            request: The user request object

        Returns:
            AsyncGenerator[PromptResult, None]: A generator of PromptResult objects
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = True

        # Call provider with request
        async for history in self.provider.generate_stream(request):
            content = history.get_full_content()
            yield PromptResult(raw_content=content)

    async def generate_raw(
        self,
        request: UserRequest,
    ) -> PromptResult:
        """
        Generate a complete raw response without parsing.

        Args:
            request: The user request object

        Returns:
            PromptResult: Contains the raw content
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = False

        # Call provider with request
        history = await self.provider.generate_completion(request)

        content = history.get_full_content()
        return PromptResult(raw_content=content)

    async def stream_structured(
        self,
        request: UserRequest,
    ) -> AsyncGenerator[ParseResult[ResponseType], None]:
        """
        Stream a response from the model and parse it into a structured object.

        Args:
            request: The user request object with response_model set

        Returns:
            AsyncGenerator[ParseResult[ResponseType], None]: A generator of ParseResult objects
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = True

        # Ensure response_model is set
        assert request.response_model is not None, "response_model must be set on the request"

        # Call provider with request
        async for history in self.provider.generate_stream(request):
            content = history.get_full_content()
            yield create_parse_result(content, request.response_model)

    async def generate_structured(
        self,
        request: UserRequest,
    ) -> ParseResult[ResponseType]:
        """
        Generate a complete response and parse it into a structured object.

        Args:
            request: The user request object with response_model set

        Returns:
            ParseResult containing the raw content, parsed content, and model instance if valid
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = False

        # Ensure response_model is set
        assert request.response_model is not None, "response_model must be set on the request"

        # Call provider with request
        history = await self.provider.generate_completion(request)

        content = history.get_full_content()
        return create_parse_result(content, request.response_model)

    async def generate(
        self,
        request: UserRequest,
    ) -> Union[PromptResult, ParseResult[T]]:
        """
        Generate a complete response from the model.

        If request.response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be returned.

        Args:
            request: The user request object

        Returns:
            PromptResult if no response_model is provided, otherwise ParseResult[T]
        """
        if request.response_model is not None:
            return await self.generate_structured(request)
        return await self.generate_raw(request)

    def stream(
        self,
        request: UserRequest,
    ) -> Union[
        AsyncGenerator[PromptResult, None], AsyncGenerator[ParseResult[T], None]
    ]:
        """
        Stream a response from the model.

        If request.response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be streamed.

        Args:
            request: The user request object

        Returns:
            AsyncGenerator of PromptResult if no response_model is provided,
            otherwise AsyncGenerator of ParseResult[T]
        """
        if request.response_model is not None:
            return self.stream_structured(request)
        return self.stream_raw(request)
