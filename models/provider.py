from abc import ABC, abstractmethod
from typing import AsyncGenerator


class Provider(ABC):
    @abstractmethod
    async def generate(self, model: str, messages: list[dict], response_model: type):
        pass

    @abstractmethod
    def stream(
        self, model: str, messages: list[dict], response_model: type
    ) -> AsyncGenerator[dict, None]:
        pass
