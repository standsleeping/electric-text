from electric_text.providers.model_providers.openai.functions.process_schema_for_openai import (
    process_schema_for_openai,
)


def test_removes_default_values() -> None:
    # Sample schema with default values
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The title of the poem"},
            "author": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "The name of the poet",
            },
            "themes": {
                "anyOf": [
                    {"type": "array", "items": {"type": "string", "default": ""}},
                    {"type": "null"},
                ],
                "default": None,
                "description": "List of themes",
            },
        },
    }

    # Process the schema
    processed = process_schema_for_openai(schema)

    # Check that default is removed from the root level
    assert "default" not in processed

    # Check that default is removed from properties
    assert "default" not in processed["properties"]["author"]
    assert "default" not in processed["properties"]["themes"]

    # Check that default is removed from nested items
    themes_anyof = processed["properties"]["themes"]["anyOf"][0]
    assert "default" not in themes_anyof["items"]
