from typing import AsyncGenerator, Protocol, TypeVar

T = TypeVar('T')

class Provider(Protocol):
    async def generate(self, model: str, messages: list[dict[str, str]], response_model: type[T]) -> T:
        ...

    async def stream(
        self, model: str, messages: list[dict[str, str]], response_model: type[T]
    ) -> AsyncGenerator[T, None]:
        ...