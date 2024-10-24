import os
from openai import AsyncOpenAI
from instructor import from_openai, Mode
from ..provider import Provider


class ProviderImplementation(Provider):
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    def __init__(self, config):
        self.client = from_openai(
            AsyncOpenAI(
                base_url=config.get("base_url", self.BASE_URL),
                api_key="required-but-not-used",
            ),
            mode=Mode.JSON,
        )

    async def stream(self, model, messages, response_model):
        extraction_stream = self.client.chat.completions.create_partial(
            model=model,
            messages=messages,
            response_model=response_model,
            stream=True,
        )

        async for extraction in extraction_stream:
            yield extraction

    async def generate(self, model, messages, response_model):
        return await self.client.chat.completions.create(
            model=model, messages=messages, response_model=response_model
        )
