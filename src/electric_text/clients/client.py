import importlib
from typing import (
    AsyncGenerator,
    cast,
    Any,
)

from electric_text.providers import ModelProvider

from electric_text.clients.data import PromptResult, ResponseModel, UserRequest, ProviderResponse
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
    ) -> AsyncGenerator[ProviderResponse[None], None]:
        """
        Stream a raw response from the model without parsing.

        Args:
            request: The user request object

        Returns:
            AsyncGenerator[ProviderResponse[None], None]: A generator of ProviderResponse objects
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = True

        # Call provider with request
        async for history in self.provider.generate_stream(request):
            content = history.get_full_content()
            prompt_result = PromptResult(raw_content=content)
            yield ProviderResponse.from_prompt_result(prompt_result)

    async def generate_raw(
        self,
        request: UserRequest,
    ) -> ProviderResponse[None]:
        """
        Generate a complete raw response without parsing.

        Args:
            request: The user request object

        Returns:
            ProviderResponse[None]: Contains the raw content
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = False

        # Call provider with request
        history = await self.provider.generate_completion(request)

        content = history.get_full_content()
        prompt_result = PromptResult(raw_content=content)
        return ProviderResponse.from_prompt_result(prompt_result)

    async def stream_structured(
        self,
        request: UserRequest,
    ) -> AsyncGenerator[ProviderResponse[Any], None]:
        """
        Stream a response from the model and parse it into a structured object.

        Args:
            request: The user request object with response_model set

        Returns:
            AsyncGenerator[ProviderResponse[Any], None]: A generator of ProviderResponse objects
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = True

        # Ensure response_model is set
        assert request.response_model is not None, (
            "response_model must be set on the request"
        )

        # Call provider with request
        async for history in self.provider.generate_stream(request):
            content = history.get_full_content()
            parse_result = create_parse_result(content, request.response_model)
            yield ProviderResponse.from_parse_result(parse_result)

    async def generate_structured(
        self,
        request: UserRequest,
    ) -> ProviderResponse[Any]:
        """
        Generate a complete response and parse it into a structured object.

        Args:
            request: The user request object with response_model set

        Returns:
            ProviderResponse[Any]: Contains the raw content, parsed content, and model instance if valid
        """
        # Ensure request has the correct provider and stream flag
        request.provider_name = self.provider_name
        request.stream = False

        # Ensure response_model is set
        assert request.response_model is not None, (
            "response_model must be set on the request"
        )

        # Call provider with request
        history = await self.provider.generate_completion(request)

        content = history.get_full_content()
        parse_result = create_parse_result(content, request.response_model)
        return ProviderResponse.from_parse_result(parse_result)

    async def generate(
        self,
        request: UserRequest,
    ) -> ProviderResponse[ResponseModel]:
        """
        Generate a complete response from the model.

        If request.response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be returned.

        Args:
            request: The user request object

        Returns:
            ProviderResponse[ResponseModel]: A unified response wrapper
        """
        if request.response_model is not None:
            structured_result = await self.generate_structured(request)
            return cast(ProviderResponse[ResponseModel], structured_result)
        raw_result = await self.generate_raw(request)
        return cast(ProviderResponse[ResponseModel], raw_result)

    def stream(
        self,
        request: UserRequest,
    ) -> AsyncGenerator[ProviderResponse[ResponseModel], None]:
        """
        Stream a response from the model.

        If request.response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be streamed.

        Args:
            request: The user request object

        Returns:
            AsyncGenerator[ProviderResponse[ResponseModel], None]: A generator of unified response wrappers
        """
        if request.response_model is not None:
            structured_stream = self.stream_structured(request)
            return cast(AsyncGenerator[ProviderResponse[ResponseModel], None], structured_stream)
        raw_stream = self.stream_raw(request)
        return cast(AsyncGenerator[ProviderResponse[ResponseModel], None], raw_stream)
