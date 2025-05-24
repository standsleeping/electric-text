from typing import List

from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
    ToolCallData,
)


def format_content_blocks(*, content_blocks: List[ContentBlock]) -> str:
    """Format a list of content blocks for output.

    Args:
        content_blocks: The list of ContentBlock objects to format

    Returns:
        Formatted string ready for output
    """
    if not content_blocks:
        return ""

    formatted_parts = []
    for block in content_blocks:
        formatted_parts.append(format_single_content_block(content_block=block))

    return "\n".join(formatted_parts)


def format_single_content_block(*, content_block: ContentBlock) -> str:
    """Format a single content block for output.

    Args:
        content_block: The ContentBlock to format

    Returns:
        Formatted string for this content block
    """
    match content_block.type:
        case ContentBlockType.TEXT:
            text_data = content_block.data
            if isinstance(text_data, TextData):
                return text_data.text
            return str(text_data)

        case ContentBlockType.TOOL_CALL:
            tool_data = content_block.data
            if isinstance(tool_data, ToolCallData):
                return f"TOOL CALL: {tool_data.name}\nINPUTS: {tool_data.input_json_string}"
            return str(tool_data)

        case _:
            return f"UNKNOWN CONTENT BLOCK: {content_block}"
