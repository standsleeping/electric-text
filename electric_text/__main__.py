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

    country_response = await country_provider.query_complete(
        "Let's hear about France",
        response_type=CountryInfo,
    )

    print(f"Complete country response: {country_response}")

    await asyncio.sleep(1)

    async for chunk in country_provider.query_stream(
        "Tell me about Spain",
        response_type=CountryInfo,
    ):
        print(f"Chunk: {chunk}")

    weather_response = await weather_provider.query_complete(
        "What's the forecast in Paris?",
        response_type=WeatherInfo,
    )

    print(f"Complete weather response: {weather_response}")

    await asyncio.sleep(1)

    async for chunk in weather_provider.query_stream(
        "What's the weather like in Tokyo?",
        response_type=WeatherInfo,
    ):
        print(f"Chunk: {chunk}")


if __name__ == "__main__":
    asyncio.run(main())
