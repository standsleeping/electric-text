"""
Configuration Source: Environment variables
Prompt Config: Yes (prose_to_schema)
Streaming: No
Tool Usage: None
Output Structure: Structured
"""

import pytest
import json

from electric_text.prompting.functions.generate import generate
from tests.boundaries import (
    mock_boundaries,
    ollama_api_response,
)


@pytest.mark.asyncio
async def test_structured():
    """System test: structured output without streaming"""

    complete_data = {
        "response_annotation": "A schema for car data with weight, cost, and range",
        "created_json_schema_definition": {
            "type": "object",
            "properties": {
                "weight_pounds": {
                    "type": "integer",
                    "description": "Weight in pounds",
                },
                "cost_dollars": {
                    "type": "integer",
                    "description": "Cost in dollars",
                },
                "range_miles": {"type": "integer", "description": "Range in miles"},
            },
            "required": ["weight_pounds", "cost_dollars", "range_miles"],
            "additionalProperties": False,
        },
    }

    complete_json = json.dumps(complete_data)

    mocks = {
        "http://localhost:11434/api/chat": ollama_api_response(complete_json),
    }

    with mock_boundaries(
        http_mocks=mocks,
        env_vars={
            "ELECTRIC_TEXT_USER_PROMPT_DIRECTORY": "examples/prompt_configs",
        },
    ):
        result = await generate(
            text_input="The car weighs 5,000 pounds, costs $25,000, and has a range of 400 miles.",
            provider_name="ollama",
            model_name="llama3.1:8b",
            prompt_name="prose_to_schema",
            stream=False,
            log_level="ERROR",
        )

        data = result.data

        assert data.is_valid
        assert data.schema_name == "SchemaResponse"
        assert data.validation_error is None
        assert data.data == complete_data 