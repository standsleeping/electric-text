import importlib
from typing import AsyncGenerator
from electric_text.clients.data.validation_model import ValidationModel
from electric_text.providers import ModelProvider
from electric_text.clients.data.client_request import ClientRequest
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.clients.data import ClientResponse
from electric_text.clients.data.default_output_schema import DefaultOutputSchema
from electric_text.clients.functions.history_to_client_response import (
    history_to_client_response,
)
from electric_text.clients.functions.convert_to_provider_request import (
    convert_to_provider_request,
)


class Client:
    provider: ModelProvider
    provider_name: str

    def __init__(
        self,
        provider_name: str,
        config: dict[str, str] = {},
        http_logging_enabled: bool = False,
        http_log_dir: str = "./http_logs",
    ) -> None:
        self.provider_name = provider_name
        provider_module = f"electric_text.providers.model_providers.{provider_name}"
        module = importlib.import_module(provider_module)
        provider_class = getattr(module, f"{provider_name.title()}Provider")

        # Pass HTTP logging config to provider
        provider_config = {
            **config,
            "http_logging_enabled": http_logging_enabled,
            "http_log_dir": http_log_dir,
        }
        self.provider = provider_class(**provider_config)

    async def stream_raw[OutputSchema: ValidationModel](
        self, request: ClientRequest[OutputSchema]
    ) -> AsyncGenerator[ClientResponse[OutputSchema], None]:
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
            yield ClientResponse[OutputSchema](stream_history=history)

    async def generate_raw[OutputSchema: ValidationModel](
        self,
        request: ClientRequest[OutputSchema],
    ) -> ClientResponse[OutputSchema]:
        """
        Generate a complete raw response without parsing.

        Args:
            request: the request to the client

        Returns:
            ClientResponse[None]: Contains the raw content
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Call provider with request
        history: StreamHistory = await self.provider.generate_completion(
            provider_request
        )

        return ClientResponse[OutputSchema](stream_history=history)

    async def stream_structured[OutputSchema: ValidationModel](
        self,
        request: ClientRequest[OutputSchema],
    ) -> AsyncGenerator[ClientResponse[OutputSchema], None]:
        """
        Stream a response from the model and parse it into a structured object.

        Args:
            request: the request to the client with output_schema set

        Returns:
            AsyncGenerator[ClientResponse[Any], None]: A generator of ClientResponse objects
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Ensure output_schema is set
        assert request.output_schema is not DefaultOutputSchema, "missing output_schema"

        # Call provider with request
        async for history in self.provider.generate_stream(provider_request):
            response: ClientResponse[OutputSchema] = await history_to_client_response(
                history, request.output_schema
            )

            yield response

    async def generate_structured[OutputSchema: ValidationModel](
        self,
        request: ClientRequest[OutputSchema],
    ) -> ClientResponse[OutputSchema]:
        """
        Generate a complete response and parse it into a structured object.

        Args:
            request: the request to the client with output_schema set

        Returns:
            ClientResponse[Any]: Contains the raw content, parsed content, and model instance if valid
        """
        provider_request: ProviderRequest = convert_to_provider_request(request)

        # Ensure output_schema is set
        assert request.output_schema is not None, "missing output_schema"

        # Call provider with request
        history = await self.provider.generate_completion(provider_request)

        return await history_to_client_response(history, request.output_schema)

    async def generate[OutputSchema: ValidationModel](
        self,
        request: ClientRequest[OutputSchema],
    ) -> ClientResponse[OutputSchema]:
        """
        Generate a complete response from the model.

        If request.output_schema is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be returned.

        Args:
            request: the request to the client

        Returns:
            ClientResponse[OutputSchema]: A unified response wrapper
        """
        if request.output_schema is not DefaultOutputSchema:
            structured_result: ClientResponse[
                OutputSchema
            ] = await self.generate_structured(request)
            return structured_result

        raw_result: ClientResponse[OutputSchema] = await self.generate_raw(request)

        return raw_result

    def stream[OutputSchema: ValidationModel](
        self,
        request: ClientRequest[OutputSchema],
    ) -> AsyncGenerator[ClientResponse[OutputSchema], None]:
        """
        Stream a response from the model.

        If request.output_schema is provided, the response will be parsed into a structured object.
        Otherwise, the raw response will be streamed.

        Args:
            request: the request to the client

        Returns:
            AsyncGenerator[ClientResponse[OutputSchema], None]: A generator of unified response wrappers
        """
        if request.output_schema is not DefaultOutputSchema:
            structured_stream = self.stream_structured(request)
            return structured_stream

        raw_stream = self.stream_raw(request)
        return raw_stream
