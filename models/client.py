import importlib
from typing import AsyncGenerator, TypeVar
from .provider import Provider

T = TypeVar("T")


class Client:
    provider: Provider

    def __init__(self, provider_name: str, config: dict[str, str] = {}) -> None:
        provider_module = f"models.providers.{provider_name}"
        module = importlib.import_module(provider_module, package="models")
        provider_class = getattr(module, "ProviderImplementation")
        self.provider = provider_class(config)

    async def stream(
        self, model: str, messages: list[dict[str, str]], response_model: type[T]
    ) -> AsyncGenerator[T, None]:
        async for chunk in self.provider.stream(model, messages, response_model):
            yield chunk

    async def generate(
        self, model: str, messages: list[dict[str, str]], response_model: type[T]
    ) -> T:
        return await self.provider.generate(model, messages, response_model)
