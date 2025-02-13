import asyncio
from pydantic import BaseModel, Field
from models.client import Client, ParseResult
from typing import AsyncIterator


class CountryInfo(BaseModel):
    name: str = Field(description="The name of the country")
    capital: str = Field(description="The capital city of the country")
    languages: list[str] = Field(description="Official languages spoken in the country")


class WeatherInfo(BaseModel):
    temperature: float = Field(description="Current temperature")
    conditions: str = Field(description="Weather conditions (e.g., sunny, rainy)")
    humidity: int = Field(description="Current humidity percentage")


async def main() -> None:
    SYSTEM_MESSAGE = {"role": "system", "content": "You are a helpful assistant."}

    # Step 1: Create clients for each response type
    country_client: Client[CountryInfo] = Client(provider_name="ollama")
    weather_client: Client[WeatherInfo] = Client(provider_name="ollama")

    # Step 2: Register schemas with the providers
    country_client.provider.register_schema(
        CountryInfo, CountryInfo.model_json_schema()
    )

    weather_client.provider.register_schema(
        WeatherInfo, WeatherInfo.model_json_schema()
    )

    # Step 3: Query about France
    country_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "Let's hear about France"},
    ]

    country_response = await country_client.generate(
        model="llama3.1:8b",
        messages=country_messages,
        response_model=CountryInfo,
    )

    print(f"Complete country response: {country_response}")

    await asyncio.sleep(1)

    # Step 4: Stream information about Spain
    spain_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "Tell me about Spain"},
    ]

    async for chunk in country_client.stream(
        model="llama3.1:8b",
        messages=spain_messages,
        response_model=CountryInfo,
    ):
        print(f"Chunk: {chunk}")

    # Step 5: Query weather in Paris
    weather_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "What's the forecast in Paris?"},
    ]

    weather_response = await weather_client.generate(
        model="llama3.1:8b",
        messages=weather_messages,
        response_model=WeatherInfo,
    )

    print(f"Complete weather response: {weather_response}")

    await asyncio.sleep(1)

    # Step 6: Stream weather in Tokyo
    tokyo_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "What's the weather like in Tokyo?"},
    ]

    # Here, we use AsyncIterator to properly type the stream.
    # This allows us to infer weather_chunk as ParseResult[WeatherInfo] in the async for loop.
    stream: AsyncIterator[ParseResult[WeatherInfo]] = weather_client.stream(
        model="llama3.1:8b",
        messages=tokyo_messages,
        response_model=WeatherInfo,
    )

    async for weather_chunk in stream:
        print(f"Chunk: {weather_chunk}\n\n")


if __name__ == "__main__":
    asyncio.run(main())
