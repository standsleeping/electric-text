import importlib
from typing import (
    AsyncGenerator,
    cast,
    Any,
)
from electric_text.providers import ModelProvider
from electric_text.clients.data.client_request import ClientRequest
from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.clients.functions.create_parse_result import create_parse_result
from electric_text.clients.functions.convert_to_provider_request import (
    convert_to_provider_request,
)
from electric_text.clients.data import (
    PromptResult,
    ResponseModel,
    ClientResponse,
)


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
        request: ClientRequest,
    ) -> AsyncGenerator[ClientResponse[None], None]:
        """
        Stream a raw response from the model without parsing.

        Args:
            request: the request to the client

        Returns:
            AsyncGenerator[ClientResponse[None], None]: A generator of ClientResponse objects
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Call provider with request
        async for history in self.provider.generate_stream(provider_request):
            content = history.get_full_content()
            prompt_result = PromptResult(raw_content=content)
            yield ClientResponse.from_prompt_result(prompt_result)

    async def generate_raw(
        self,
        request: ClientRequest,
    ) -> ClientResponse[None]:
        """
        Generate a complete raw response without parsing.

        Args:
            request: the request to the client

        Returns:
            ClientResponse[None]: Contains the raw content
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Call provider with request
        history = await self.provider.generate_completion(provider_request)

        content = history.get_full_content()
        prompt_result = PromptResult(raw_content=content)
        return ClientResponse.from_prompt_result(prompt_result)

    async def stream_structured(
        self,
        request: ClientRequest,
    ) -> AsyncGenerator[ClientResponse[Any], None]:
        """
        Stream a response from the model and parse it into a structured object.

        Args:
            request: the request to the client with response_model set

        Returns:
            AsyncGenerator[ClientResponse[Any], None]: A generator of ClientResponse objects
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Ensure response_model is set
        assert request.response_model is not None, (
            "response_model must be set on the request"
        )

        # Call provider with request
        async for history in self.provider.generate_stream(provider_request):
            content = history.get_full_content()
            parse_result = create_parse_result(content, request.response_model)
            yield ClientResponse.from_parse_result(parse_result)

    async def generate_structured(
        self,
        request: ClientRequest,
    ) -> ClientResponse[Any]:
        """
        Generate a complete response and parse it into a structured object.

        Args:
            request: the request to the client with response_model set

        Returns:
            ClientResponse[Any]: Contains the raw content, parsed content, and model instance if valid
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Ensure response_model is set
        assert request.response_model is not None, (
            "response_model must be set on the request"
        )

        # Call provider with request
        history = await self.provider.generate_completion(provider_request)

        content = history.get_full_content()
        parse_result = create_parse_result(content, request.response_model)
        return ClientResponse.from_parse_result(parse_result)

    async def generate(
        self,
        request: ClientRequest,
    ) -> ClientResponse[ResponseModel]:
        """
        Generate a complete response from the model.

        If request.response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be returned.

        Args:
            request: the request to the client

        Returns:
            ClientResponse[ResponseModel]: A unified response wrapper
        """
        if request.response_model is not None:
            structured_result = await self.generate_structured(request)
            return cast(ClientResponse[ResponseModel], structured_result)
        raw_result = await self.generate_raw(request)
        return cast(ClientResponse[ResponseModel], raw_result)

    def stream(
        self,
        request: ClientRequest,
    ) -> AsyncGenerator[ClientResponse[ResponseModel], None]:
        """
        Stream a response from the model.

        If request.response_model is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be streamed.

        Args:
            request: the request to the client

        Returns:
            AsyncGenerator[ClientResponse[ResponseModel], None]: A generator of unified response wrappers
        """
        if request.response_model is not None:
            structured_stream = self.stream_structured(request)
            return cast(
                AsyncGenerator[ClientResponse[ResponseModel], None], structured_stream
            )
        raw_stream = self.stream_raw(request)
        return cast(AsyncGenerator[ClientResponse[ResponseModel], None], raw_stream)
