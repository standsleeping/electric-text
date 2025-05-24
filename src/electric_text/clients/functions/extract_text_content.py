from typing import List

from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
)


def extract_text_content(*, content_blocks: List[ContentBlock]) -> str:
    """Extract text content from a list of content blocks.

    Args:
        content_blocks: The list of ContentBlock objects to extract text from

    Returns:
        Concatenated text content from all text blocks
    """
    if not content_blocks:
        return ""

    text_parts = []
    for block in content_blocks:
        if block.type == ContentBlockType.TEXT:
            text_data = block.data
            if isinstance(text_data, TextData):
                text_parts.append(text_data.text)
            else:
                text_parts.append(str(text_data))

    return "\n".join(text_parts)