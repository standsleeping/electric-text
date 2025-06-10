"""
Configuration Source: Environment variables
Prompt Config: Yes (prose_to_schema)
Streaming: Yes
Tool Usage: None
Output Structure: Structured
"""

import pytest
import json

from electric_text.prompting.functions.generate import generate
from tests.boundaries import (
    mock_boundaries,
    ollama_streaming_response,
)


@pytest.mark.asyncio
async def test_structured_streaming():
    """System test: structured output with streaming enabled"""

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

    json_chunks = [
        complete_json[:50],
        complete_json[50:100],
        complete_json[100:150],
        complete_json[150:200],
        complete_json[200:250],
        complete_json[250:300],
        complete_json[300:350],
        complete_json[350:400],
        complete_json[400:450],
        complete_json[450:500],
    ]

    mocks = {
        "http://localhost:11434/api/chat": ollama_streaming_response(
            chunks=json_chunks
        ),
    }

    with mock_boundaries(
        http_mocks=mocks,
        env_vars={
            "ELECTRIC_TEXT_USER_PROMPT_DIRECTORY": "examples/prompt_configs",
        },
    ):
        result_generator = await generate(
            text_input="Some text",
            provider_name="ollama",
            model_name="llama3.1:8b",
            prompt_name="prose_to_schema",
            stream=True,
            log_level="ERROR",
        )

        chunks = []
        async for chunk in result_generator:
            chunks.append(chunk)

        last = chunks[-1]

        data = last.data

        assert data.is_valid
        assert data.schema_name == "SchemaResponse"
        assert data.validation_error is None
        assert data.data == complete_data
