import json
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory

# if not line.strip():
#     continue

# # Anthropic format: "event: <event_type>\ndata: <json_data>\n\n"
# if line.startswith("data:"):
#     data_str = line[5:].strip()

#     try:
#         data = json.loads(data_str)

#         if "delta" in data and "text" in data["delta"]:
#             content = data["delta"]["text"]
#             stream_chunk = StreamChunk(
#                 type=StreamChunkType.CONTENT_CHUNK,
#                 raw_line=line,
#                 parsed_data=data,
#                 content=content,
#             )
#             self.stream_history.add_chunk(stream_chunk)
#             yield self.stream_history
#         elif "type" in data and data["type"] == "message_stop":
#             # Final message indicating completion
#             stream_chunk = StreamChunk(
#                 type=StreamChunkType.COMPLETION_END,
#                 raw_line=line,
#                 parsed_data=data,
#                 content="",
#             )
#             self.stream_history.add_chunk(stream_chunk)
#             yield self.stream_history
#         elif "error" in data:
#             # Handle API errors
#             error_chunk = StreamChunk(
#                 type=StreamChunkType.FORMAT_ERROR,
#                 raw_line=line,
#                 error=data["error"]["message"],
#             )
#             self.stream_history.add_chunk(error_chunk)
#             yield self.stream_history

#     except json.JSONDecodeError as e:
#         error_chunk = StreamChunk(
#             type=StreamChunkType.PARSE_ERROR,
#             raw_line=line,
#             error=str(e),
#         )
#         self.stream_history.add_chunk(error_chunk)
#         yield self.stream_history
# else:
#     error_chunk = StreamChunk(
#         type=StreamChunkType.UNHANDLED_LINE,
#         raw_line=line,
#         error=f"Unhandled line: {line}",
#     )
#     self.stream_history.add_chunk(error_chunk)
#     yield self.stream_history

def process_stream_response(
    raw_line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a stream response line into a StreamHistory.

    This function handles individual stream response chunks from Ollama
    and adds the appropriate StreamChunk objects to the provided history.

    Args:
        raw_line: The raw line received from the stream
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory with the new chunk(s) added
    """
    abc = 123
    return history
