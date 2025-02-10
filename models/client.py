import importlib
import json
from typing import AsyncGenerator, Generic
from models.provider import ModelProvider, ResponseType


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
    ) -> AsyncGenerator[ResponseType, None]:
        async for chunk in self.provider.query_stream(messages, response_model, model):
            content = json.loads(chunk["message"]["content"])
            yield response_model(**content)

    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_model: type[ResponseType],
    ) -> ResponseType:
        return await self.provider.query_complete(messages, response_model, model)
