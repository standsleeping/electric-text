import json
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def categorize_stream_line(line: str) -> StreamChunk:
    """
    Categorize a stream line from an LLM provider into a StreamChunk.

    Args:
        line: Raw line from the stream

    Returns:
        StreamChunk containing the categorized data
    """
    if line == "":
        return StreamChunk(StreamChunkType.EMPTY_LINE, line)

    if line.startswith("event: "):
        event_type = line[6:].strip()
        try:
            chunk_type = next(ct for ct in StreamChunkType if ct.value == event_type)
            return StreamChunk(chunk_type, line)
        except StopIteration:
            return StreamChunk(StreamChunkType.INVALID_FORMAT, line)

    if line.startswith("data: [DONE]"):
        return StreamChunk(StreamChunkType.STREAM_DONE, line)

    if not line.startswith("data: "):
        return StreamChunk(StreamChunkType.INVALID_FORMAT, line)

    try:
        data = json.loads(line[6:])  # Remove "data: " prefix
        data_type = data.get("type")

        if not data_type:
            return StreamChunk(StreamChunkType.INVALID_FORMAT, line)

        match data_type:
            # Response lifecycle events
            case StreamChunkType.RESPONSE_CREATED.value:
                # data['response']['output'] should be []
                return StreamChunk(
                    StreamChunkType.RESPONSE_CREATED,
                    line,
                    parsed_data=data,
                )
            case StreamChunkType.RESPONSE_IN_PROGRESS.value:
                # data['response']['output'] should be []
                return StreamChunk(
                    StreamChunkType.RESPONSE_IN_PROGRESS,
                    line,
                    parsed_data=data,
                )
            case StreamChunkType.RESPONSE_COMPLETED.value:
                return StreamChunk(
                    StreamChunkType.RESPONSE_COMPLETED,
                    line,
                    parsed_data=data,
                )
            case StreamChunkType.RESPONSE_FAILED.value:
                return StreamChunk(
                    StreamChunkType.RESPONSE_FAILED,
                    line,
                    parsed_data=data,
                )
            case StreamChunkType.RESPONSE_INCOMPLETE.value:
                return StreamChunk(
                    StreamChunkType.RESPONSE_INCOMPLETE,
                    line,
                    parsed_data=data,
                )

            # Output item events
            case StreamChunkType.OUTPUT_ITEM_ADDED.value:
                # data keys: ['type', 'output_index', 'item']
                # item = data["item"] # item keys: ['id', 'type', 'status', 'content', 'role']
                # content = item['content']
                return StreamChunk(
                    StreamChunkType.OUTPUT_ITEM_ADDED,
                    line,
                    parsed_data=data,
                )
            case StreamChunkType.OUTPUT_ITEM_DONE.value:
                return StreamChunk(
                    StreamChunkType.OUTPUT_ITEM_DONE,
                    line,
                    parsed_data=data,
                )

            # Content part events
            case StreamChunkType.CONTENT_PART_ADDED.value:
                return StreamChunk(
                    StreamChunkType.CONTENT_PART_ADDED,
                    line,
                    parsed_data=data,
                )
            case StreamChunkType.CONTENT_PART_DONE.value:
                return StreamChunk(
                    StreamChunkType.CONTENT_PART_DONE,
                    line,
                    parsed_data=data,
                )

            # Output text events
            case StreamChunkType.OUTPUT_TEXT_DELTA.value:
                # data keys: ['type', 'item_id', 'output_index', 'content_index', 'delta']
                delta = data["delta"]
                return StreamChunk(
                    StreamChunkType.OUTPUT_TEXT_DELTA,
                    line,
                    parsed_data=data,
                    content=delta,
                )
            case StreamChunkType.OUTPUT_TEXT_DONE.value:
                return StreamChunk(
                    StreamChunkType.OUTPUT_TEXT_DONE,
                    line,
                    parsed_data=data,
                )

            # Text annotation events
            case StreamChunkType.TEXT_ANNOTATION_ADDED.value:
                return StreamChunk(
                    StreamChunkType.TEXT_ANNOTATION_ADDED,
                    line,
                    parsed_data=data,
                )

            case _:
                try:
                    chunk_type = next(
                        ct for ct in StreamChunkType if ct.value == data_type
                    )
                    return StreamChunk(chunk_type, line, parsed_data=data)
                except StopIteration:
                    return StreamChunk(StreamChunkType.INVALID_FORMAT, line)

    except json.JSONDecodeError as e:
        return StreamChunk(StreamChunkType.PARSE_ERROR, line, error=str(e))
