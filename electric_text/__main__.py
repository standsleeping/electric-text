import asyncio
from models import Client
from typing import AsyncGenerator
from pydantic import BaseModel


class Translation(BaseModel):
    language: str
    one: str
    two: str
    three: str


messages = [
    {
        "role": "user",
        "content": "Create a Spanish translation for 'one, two, three, four'.",
    }
]

MODEL = "llama3.2:3b"


async def first_example() -> None:
    client = Client(provider_name="ollama")

    print("Streaming:")

    extraction_stream: AsyncGenerator[Translation, None] = client.stream(
        model=MODEL, messages=messages, response_model=Translation
    )

    async for extraction in extraction_stream:
        print(extraction.model_dump_json(indent=2))

    print("All at once:")

    all_at_once = await client.generate(
        model=MODEL, messages=messages, response_model=Translation
    )

    print(all_at_once.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(first_example())
