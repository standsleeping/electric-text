from typing import AsyncGenerator, Protocol, TypeVar

T = TypeVar("T")

msg_type = dict[str, str]


class Provider(Protocol):
    # Async because we want to await the result.
    # Example: `result = await generate(...)`.
    async def generate(
        self, model: str, messages: list[msg_type], response_model: type[T]
    ) -> T: ...

    # No async here because we want to yield from the stream.
    # Example: `async for chunk in stream(...)`.
    def stream(
        self, model: str, messages: list[msg_type], response_model: type[T]
    ) -> AsyncGenerator[T, None]: ...
