"""Constants and type definitions for capabilities."""

from typing import Dict, Any, Union


# Standard capability names
STRUCTURED_OUTPUT = "structured_output"
PREFILL = "prefill"
STREAMING = "streaming"


# Provider-specific format definitions
STRUCTURED_OUTPUT_FORMATS: Dict[str, Dict[str, Union[str, bool, Dict[str, str]]]] = {
    "ollama": {
        "param": "format_schema",
        "schema_method": "model_json_schema",
    },
    "anthropic": {
        "param": "structured_prefill",
        "value": True,
    },
    "openai": {
        "param": "response_format",
        "value": {"type": "json_object"},
    },
}


PREFILL_FORMATS: Dict[str, Dict[str, Any]] = {
    "anthropic": {
        "param": "prefill_content",  # Actual content parameter
        "structured_param": "structured_prefill",  # Flag for structured prefill
        "structured_value": True,  # Default value for structured prefill flag
    }
}


# Default provider capabilities
DEFAULT_PROVIDER_CAPABILITIES = {
    "ollama": {STRUCTURED_OUTPUT, STREAMING},
    "anthropic": {
        STRUCTURED_OUTPUT,
        STREAMING,
        PREFILL,
    },
    "openai": {
        STRUCTURED_OUTPUT,
        STREAMING,
    },
}
