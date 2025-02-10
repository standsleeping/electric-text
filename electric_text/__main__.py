import asyncio
from pydantic import BaseModel, Field
from models.providers.ollama import OllamaProvider


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

    country_provider: OllamaProvider[CountryInfo] = OllamaProvider()
    country_provider.register_schema(CountryInfo, CountryInfo.model_json_schema())

    weather_provider: OllamaProvider[WeatherInfo] = OllamaProvider()
    weather_provider.register_schema(WeatherInfo, WeatherInfo.model_json_schema())

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
