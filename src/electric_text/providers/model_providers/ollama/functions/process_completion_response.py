from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.model_providers.ollama.functions.process_content import (
    process_content,
)
from electric_text.providers.model_providers.ollama.functions.process_tool_calls import (
    process_tool_calls,
)
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)


def process_completion_response(
    response: ModelResponse,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a completion response into a StreamHistory.

    Args:
        response: ModelResponse to process
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory containing all chunks from the response
    """
    # Process content if present
    if response.message.content:
        history.add_chunk(process_content(response))

    # Process tool calls if present
    if response.message.tool_calls:
        for chunk in process_tool_calls(response):
            history.add_chunk(chunk)

    return history
