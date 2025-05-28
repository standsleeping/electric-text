import json
from pydantic import BaseModel, ValidationError

from electric_text.clients.data.client_response import ClientResponse
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.prompting.data.system_output_type import SystemOutputType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
    ToolCallData,
)
from electric_text.prompting.functions.output_conversion.client_response_to_system_output import (
    client_response_to_system_output,
)


class SampleModel(BaseModel):
    name: str
    value: int


def test_client_response_to_system_output_tool_call():
    """Converts ClientResponse with tool call to TOOL_CALL SystemOutput."""
    history = StreamHistory()

    tool_call_data = ToolCallData(
        name="test_tool",
        input={"param1": "value1", "param2": 42},
        input_json_string='{"param1": "value1", "param2": 42}',
    )

    tool_call_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=tool_call_data,
    )

    history.content_blocks.append(tool_call_block)

    response = ClientResponse[SampleModel](stream_history=history)

    result = client_response_to_system_output(response)

    assert result.response_type == SystemOutputType.TOOL_CALL
    tool_call = result.tool_call
    assert tool_call is not None
    assert tool_call.name == "test_tool"
    assert tool_call.inputs == {"param1": "value1", "param2": 42}
    assert result.text is None
    assert result.data is None


def test_client_response_to_system_output_valid_structured_data():
    """Converts ClientResponse with valid structured data to DATA SystemOutput."""
    history = StreamHistory()

    text_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text='{"name": "test", "value": 123}'),
    )

    history.content_blocks.append(text_block)

    validated_model = SampleModel(name="test", value=123)

    response = ClientResponse[SampleModel](
        stream_history=history,
        parsed_content={"name": "test", "value": 123},
        validated_output=validated_model,
    )

    result = client_response_to_system_output(response)

    assert result.response_type == SystemOutputType.DATA
    data_output = result.data
    assert data_output is not None
    assert data_output.data == {"name": "test", "value": 123}
    assert data_output.is_valid is True
    assert data_output.schema_name == "SampleModel"
    assert data_output.validation_error is None
    assert result.text is None
    assert result.tool_call is None


def test_client_response_to_system_output_invalid_structured_data_validation_error():
    """Converts ClientResponse with validation error to invalid DATA SystemOutput."""
    history = StreamHistory()

    text_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text='{"name": "test", "value": "not_an_int"}'),
    )
    history.content_blocks.append(text_block)

    validation_error = ValidationError.from_exception_data(
        "ValidationError",
        [
            {
                "type": "int_parsing",
                "loc": ("value",),
                "msg": "Input should be a valid integer",
            }
        ],
    )

    response = ClientResponse[SampleModel](
        stream_history=history,
        parsed_content={"name": "test", "value": "not_an_int"},
        validation_error=validation_error,
    )

    result = client_response_to_system_output(response)

    assert result.response_type == SystemOutputType.DATA
    data_output = result.data
    assert data_output is not None
    assert data_output.data == {"name": "test", "value": "not_an_int"}
    assert data_output.is_valid is False
    assert data_output.schema_name is None
    assert data_output.validation_error is not None
    assert result.text is None
    assert result.tool_call is None


def test_client_response_to_system_output_invalid_structured_data_json_error():
    """Converts ClientResponse with JSON error to invalid DATA SystemOutput."""
    history = StreamHistory()

    text_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text='{"name": "test", "value":'),
    )

    history.content_blocks.append(text_block)

    json_error = json.JSONDecodeError(
        "Expecting value", '{"name": "test", "value":', 25
    )

    response = ClientResponse[SampleModel](
        stream_history=history,
        parsed_content={"name": "test", "value": None},
        json_error=json_error,
    )

    result = client_response_to_system_output(response)

    assert result.response_type == SystemOutputType.DATA
    data_output = result.data
    assert data_output is not None
    assert data_output.data == {"name": "test", "value": None}
    assert data_output.is_valid is False
    assert data_output.schema_name is None
    assert data_output.validation_error is not None
    assert result.text is None
    assert result.tool_call is None


def test_client_response_to_system_output_text_response():
    """Converts ClientResponse with text content to TEXT SystemOutput."""
    history = StreamHistory()

    text_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text="Hello, this is a simple text response!"),
    )

    history.content_blocks.append(text_block)

    response = ClientResponse[SampleModel](stream_history=history)

    result = client_response_to_system_output(response)

    assert result.response_type == SystemOutputType.TEXT
    text_output = result.text
    assert text_output is not None
    assert text_output.content == "Hello, this is a simple text response!"
    assert result.data is None
    assert result.tool_call is None


def test_client_response_to_system_output_empty_text_response():
    """Converts ClientResponse with empty content to TEXT SystemOutput."""
    history = StreamHistory()

    response = ClientResponse[SampleModel](stream_history=history)

    result = client_response_to_system_output(response)

    assert result.response_type == SystemOutputType.TEXT
    text_output = result.text
    assert text_output is not None
    assert text_output.content == ""
    assert result.data is None
    assert result.tool_call is None
