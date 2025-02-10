import asyncio
from dataclasses import dataclass
from models.providers.ollama import OllamaProvider


@dataclass
class CountryInfo:
    name: str
    capital: str
    languages: list[str]


@dataclass
class WeatherInfo:
    temperature: float
    conditions: str
    humidity: int


async def main() -> None:
    SYSTEM_MESSAGE = {"role": "system", "content": "You are a helpful assistant."}

    country_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "capital": {"type": "string"},
            "languages": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["name", "capital", "languages"],
    }

    weather_schema = {
        "type": "object",
        "properties": {
            "temperature": {"type": "number"},
            "conditions": {"type": "string"},
            "humidity": {"type": "integer"},
        },
        "required": ["temperature", "conditions", "humidity"],
    }

    country_provider: OllamaProvider[CountryInfo] = OllamaProvider()
    country_provider.register_schema(CountryInfo, country_schema)
    weather_provider: OllamaProvider[WeatherInfo] = OllamaProvider()
    weather_provider.register_schema(WeatherInfo, weather_schema)

    country_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "Let's hear about France"},
    ]

    country_response = await country_provider.query_complete(
        country_messages,
        response_type=CountryInfo,
    )

    print(f"Complete country response: {country_response}")

    await asyncio.sleep(1)

    spain_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "Tell me about Spain"},
    ]

    async for chunk in country_provider.query_stream(
        spain_messages,
        response_type=CountryInfo,
    ):
        print(f"Chunk: {chunk}")

    weather_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "What's the forecast in Paris?"},
    ]

    weather_response = await weather_provider.query_complete(
        weather_messages,
        response_type=WeatherInfo,
    )

    print(f"Complete weather response: {weather_response}")

    await asyncio.sleep(1)

    tokyo_messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": "What's the weather like in Tokyo?"},
    ]

    async for chunk in weather_provider.query_stream(
        tokyo_messages,
        response_type=WeatherInfo,
    ):
        print(f"Chunk: {chunk}")


if __name__ == "__main__":
    asyncio.run(main())
