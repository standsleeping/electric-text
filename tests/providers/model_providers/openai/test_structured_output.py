from pydantic import BaseModel, Field
from typing import List

from electric_text.providers.model_providers.openai.functions.set_text_format import (
    set_text_format,
)
from electric_text.providers.model_providers.openai.functions.camel_to_snake import (
    camel_to_snake,
)
from electric_text.providers.model_providers.openai.functions.process_schema_for_openai import (
    process_schema_for_openai,
)


# Define a schema using Pydantic (same as in the example)
class SchemaResponse(BaseModel):
    """Model representing a structured response."""

    main_topic: str = Field(
        description="The main topic extracted from the conversation"
    )

    key_points: List[str] = Field(
        description="A list of key points related to the main topic"
    )

    related_topics: List[str] = Field(
        description="A list of topics related to the main topic"
    )

    model_config = {
        "json_schema_extra": {
            "title": "TopicExtraction",  # Title is used for the schema name
            "examples": [
                {
                    "main_topic": "Climate Change",
                    "key_points": [
                        "Rising global temperatures",
                        "Melting ice caps",
                        "Extreme weather events",
                    ],
                    "related_topics": [
                        "Renewable Energy",
                        "Carbon Emissions",
                        "Conservation",
                    ],
                }
            ],
        }
    }


def test_camel_to_snake_conversion():
    """Tests camel_to_snake function correctly converts camelCase to snake_case."""
    assert camel_to_snake("TopicExtraction") == "topic_extraction"
    assert camel_to_snake("mainTopic") == "main_topic"
    assert camel_to_snake("HTTPResponse") == "http_response"
    assert camel_to_snake("already_snake") == "already_snake"
    assert camel_to_snake("MixedCase_with_snake") == "mixed_case_with_snake"


def test_process_schema_for_openai_adds_required_properties():
    """Tests process_schema_for_openai adds required properties if not specified."""
    input_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }

    processed = process_schema_for_openai(input_schema)

    assert "required" in processed
    assert sorted(processed["required"]) == ["age", "name"]


def test_process_schema_for_openai_sets_additional_properties():
    """Tests process_schema_for_openai sets additionalProperties to false if not specified."""
    input_schema = {"type": "object", "properties": {"name": {"type": "string"}}}

    processed = process_schema_for_openai(input_schema)

    assert "additionalProperties" in processed
    assert processed["additionalProperties"] is False


def test_process_schema_for_openai_removes_unsupported_keywords():
    """Tests process_schema_for_openai removes unsupported keywords like examples."""
    input_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "examples": [{"name": "John"}],
        "$comment": "This is a comment",
    }

    processed = process_schema_for_openai(input_schema)

    assert "examples" not in processed
    assert "$comment" not in processed


def test_process_schema_for_openai_processes_nested_properties():
    """Tests process_schema_for_openai processes nested object properties."""
    input_schema = {
        "type": "object",
        "properties": {
            "person": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                        },
                        "examples": [{"street": "123 Main St", "city": "Anytown"}],
                    },
                },
                "$comment": "Person information",
            }
        },
    }

    processed = process_schema_for_openai(input_schema)

    # Check that person object has required properties
    assert "required" in processed["properties"]["person"]
    assert sorted(processed["properties"]["person"]["required"]) == ["address", "name"]

    # Check that address object has required properties and no examples
    address_schema = processed["properties"]["person"]["properties"]["address"]
    assert "required" in address_schema
    assert sorted(address_schema["required"]) == ["city", "street"]
    assert "examples" not in address_schema
    assert "$comment" not in processed["properties"]["person"]


def test_set_text_format_with_pydantic_schema():
    """Tests set_text_format function with a schema from a Pydantic model."""
    # Generate the schema from the Pydantic model
    schema = SchemaResponse.model_json_schema()

    # Call the set_text_format function
    result = set_text_format(schema)

    # Validate the result structure
    assert "format" in result
    assert result["format"]["type"] == "json_schema"
    assert (
        result["format"]["name"] == "topic_extraction"
    )  # Converted from TopicExtraction
    assert result["format"]["strict"] is True
    assert "schema" in result["format"]

    # Check the schema has been processed correctly
    processed_schema = result["format"]["schema"]
    assert processed_schema["type"] == "object"
    assert processed_schema["additionalProperties"] is False
    assert "main_topic" in processed_schema["properties"]
    assert "key_points" in processed_schema["properties"]
    assert "related_topics" in processed_schema["properties"]

    # Check that examples have been removed (unsupported keyword)
    assert "examples" not in processed_schema


def test_set_text_format_with_non_strict_mode():
    """Tests set_text_format function with strict=False does not process schema."""
    schema = {
        "type": "object",
        "title": "SimpleSchema",
        "properties": {"name": {"type": "string"}},
        "examples": [{"name": "John"}],
    }

    # Call with strict=False
    result = set_text_format(schema, strict=False)

    # Check that the schema is not processed (examples are still present)
    assert "examples" in result["format"]["schema"]
    assert result["format"]["strict"] is False


def test_set_text_format_with_missing_title():
    """Tests set_text_format function with a schema missing a title."""
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}

    result = set_text_format(schema)

    # Should use default name
    assert result["format"]["name"] == "response_schema"


def test_process_schema_for_openai_handles_array_items():
    """Tests process_schema_for_openai sets additionalProperties for objects in array items."""
    input_schema = {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "explanation": {"type": "string"},
                        "output": {"type": "string"},
                    },
                },
            },
            "final_answer": {"type": "string"},
        },
    }

    processed = process_schema_for_openai(input_schema)

    # Check root object
    assert processed["additionalProperties"] is False
    assert "required" in processed

    # Check that the items object has additionalProperties: false
    steps_items = processed["properties"]["steps"]["items"]
    assert steps_items["additionalProperties"] is False
    assert "required" in steps_items
    assert sorted(steps_items["required"]) == ["explanation", "output"]


def test_process_schema_for_openai_handles_object_with_no_properties():
    """Tests process_schema_for_openai correctly handles objects with no properties specified."""
    input_schema = {
        "type": "object",
        "properties": {
            "simple_field": {"type": "string"},
            "generic_object": {"type": "object"},
        },
    }

    processed = process_schema_for_openai(input_schema)

    # Check root object
    assert processed["additionalProperties"] is False
    assert "required" in processed

    # Check generic object now has properties and required fields
    generic_obj = processed["properties"]["generic_object"]
    assert generic_obj["additionalProperties"] is False
    assert "properties" in generic_obj
    assert generic_obj["properties"] == {}
