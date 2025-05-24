from electric_text.formatting.functions.format_content_blocks import (
    format_content_blocks,
    format_single_content_block,
)
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
    ToolCallData,
)


def test_format_empty_content_blocks():
    """Returns empty string for empty content blocks list."""
    result = format_content_blocks(content_blocks=[])
    assert result == ""


def test_format_single_text_content_block():
    """Formats a single text content block."""
    content_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text="Hello, world!"),
    )

    result = format_single_content_block(content_block=content_block)
    assert result == "Hello, world!"


def test_format_single_tool_call_content_block():
    """Formats a single tool call content block."""
    content_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=ToolCallData(
            name="get_weather",
            input={"location": "Chicago"},
            input_json_string='{"location": "Chicago"}',
        ),
    )

    result = format_single_content_block(content_block=content_block)
    expected = 'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    assert result == expected


def test_format_multiple_content_blocks():
    """Formats multiple content blocks with newlines between them."""
    blocks = [
        ContentBlock(
            type=ContentBlockType.TEXT, data=TextData(text="Here's the weather:")
        ),
        ContentBlock(
            type=ContentBlockType.TOOL_CALL,
            data=ToolCallData(
                name="get_weather",
                input={"location": "Omaha"},
                input_json_string='{"location": "Omaha"}',
            ),
        ),
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="Thanks for using the weather service!"),
        ),
    ]

    result = format_content_blocks(content_blocks=blocks)
    expected = (
        "Here's the weather:\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Omaha"}\n'
        "Thanks for using the weather service!"
    )
    assert result == expected


def test_format_single_content_block_with_invalid_data_type():
    """Handles invalid data types gracefully by converting to string."""
    content_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data="invalid_data_type",  # type: ignore
    )

    result = format_single_content_block(content_block=content_block)
    assert result == "invalid_data_type"
