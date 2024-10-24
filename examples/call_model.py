import sys
import os
import asyncio
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.client import Client


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


async def main():
    client = Client(provider_name="ollama", config={"stream": True})
    response = await client.generate(
        model="llama3", messages=messages, response_model=Translation
    )
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
