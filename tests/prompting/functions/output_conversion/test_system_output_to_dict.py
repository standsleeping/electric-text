from electric_text.prompting.functions.output_conversion.system_output_to_dict import (
    system_output_to_dict,
)
from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.data.system_output_type import SystemOutputType
from electric_text.prompting.data.text_output import TextOutput
from electric_text.prompting.data.data_output import DataOutput
from electric_text.prompting.data.tool_call_output import ToolCallOutput


def test_system_output_to_dict_text():
    """Converts TEXT SystemOutput to dictionary."""
    output = SystemOutput(
        response_type=SystemOutputType.TEXT,
        text=TextOutput(content="Hello world!"),
    )

    result = system_output_to_dict(output)

    assert result == {
        "response_type": "TEXT",
        "text": {"content": "Hello world!"},
        "data": None,
        "tool_call": None,
    }


def test_system_output_to_dict_data_valid():
    """Converts valid DATA SystemOutput to dictionary."""
    output = SystemOutput(
        response_type=SystemOutputType.DATA,
        data=DataOutput(
            data={"name": "test", "value": 123},
            is_valid=True,
            schema_name="TestSchema",
        ),
    )

    result = system_output_to_dict(output)

    assert result == {
        "response_type": "DATA",
        "text": None,
        "data": {
            "data": {"name": "test", "value": 123},
            "is_valid": True,
            "schema_name": "TestSchema",
            "validation_error": None,
        },
        "tool_call": None,
    }


def test_system_output_to_dict_data_invalid():
    """Converts invalid DATA SystemOutput to dictionary."""
    output = SystemOutput(
        response_type=SystemOutputType.DATA,
        data=DataOutput(
            data={"name": "test", "value": "not_an_int"},
            is_valid=False,
            validation_error="Input should be a valid integer",
        ),
    )

    result = system_output_to_dict(output)

    assert result == {
        "response_type": "DATA",
        "text": None,
        "data": {
            "data": {"name": "test", "value": "not_an_int"},
            "is_valid": False,
            "schema_name": None,
            "validation_error": "Input should be a valid integer",
        },
        "tool_call": None,
    }


def test_system_output_to_dict_tool_call():
    """Converts TOOL_CALL SystemOutput to dictionary."""
    output = SystemOutput(
        response_type=SystemOutputType.TOOL_CALL,
        tool_call=ToolCallOutput(
            name="test_tool",
            inputs={"param1": "value1", "param2": 42},
            output="tool result",
        ),
    )

    result = system_output_to_dict(output)

    assert result == {
        "response_type": "TOOL_CALL",
        "text": None,
        "data": None,
        "tool_call": {
            "name": "test_tool",
            "inputs": {"param1": "value1", "param2": 42},
            "output": "tool result",
        },
    }
