from typing import Any, Dict, List


def process_nested_schemas(
    obj: Dict[str, Any], unsupported_keywords: List[str]
) -> None:
    """
    Recursively process nested schemas to ensure they meet OpenAI's requirements.

    Args:
        obj: The schema object to process
        unsupported_keywords: Keywords to remove from the schema
    """

    # Remove unsupported keywords
    for keyword in unsupported_keywords:
        if keyword in obj:
            del obj[keyword]

    # Set additionalProperties: false for any object type
    if obj.get("type") == "object" and "additionalProperties" not in obj:
        obj["additionalProperties"] = False

        # If it's an object with no properties, add an empty properties object
        # to satisfy OpenAI's validation that requires properties to match required
        if "properties" not in obj:
            obj["properties"] = {}

    # Process properties
    if "properties" in obj and isinstance(obj["properties"], dict):
        # Ensure all properties are required
        if "required" not in obj:
            obj["required"] = list(obj["properties"].keys())
        else:
            existing_props = set(obj["properties"].keys())
            obj["required"] = list(existing_props)

        # Process each property
        for prop_name, prop_value in obj["properties"].items():
            if isinstance(prop_value, dict):
                process_nested_schemas(prop_value, unsupported_keywords)

    # Process anyOf/oneOf/allOf
    for schema_keyword in ["anyOf", "oneOf", "allOf"]:
        if schema_keyword in obj and isinstance(obj[schema_keyword], list):
            for schema in obj[schema_keyword]:
                if isinstance(schema, dict):
                    process_nested_schemas(schema, unsupported_keywords)

    # Process items in arrays
    if "items" in obj and isinstance(obj["items"], dict):
        process_nested_schemas(obj["items"], unsupported_keywords)

    # Process definitions
    if "$defs" in obj and isinstance(obj["$defs"], dict):
        for def_name, def_value in obj["$defs"].items():
            process_nested_schemas(def_value, unsupported_keywords)
