from typing import Any, AsyncGenerator, Optional, Type

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.logging import get_logger

logger = get_logger(__name__)


async def execute_client_request(
    *,
    client: Client,
    request: ClientRequest,
    stream: bool = False,
    model_class: Optional[Type[Any]] = None,
) -> None:
    """Execute a client request with the given parameters, handling streaming and output.

    Args:
        client: Client instance to use for the request
        request: The ClientRequest to execute
        stream: Whether to stream the response
        model_class: Optional model class for structured outputs
    """

    # Handle non-streaming execution
    if not stream:
        response: ClientResponse[Any] = await client.generate(request=request)
        content = ""
        if response.prompt_result and response.prompt_result.content_blocks:
            from electric_text.providers.functions.format_content_blocks import format_content_blocks
            content = format_content_blocks(content_blocks=response.prompt_result.content_blocks)
        
        is_valid = response.parse_result.is_valid if response.parse_result else False
        parsed_model = response.parse_result.model if response.parse_result else None
        
        if model_class and is_valid and parsed_model:
            formatted_model = parsed_model.model_dump_json(indent=2)
            print(f"RESULT (STRUCTURED): {parsed_model}\n{formatted_model}")
        else:
            if content:
                print(f"RESULT (UNSTRUCTURED):\n{content}")
            else:
                print("RESULT (UNSTRUCTURED): [No content available]")
        return

    # Handle streaming execution - choose appropriate streaming method
    if request.response_model is not None:
        # Use structured streaming for requests with response models
        stream_generator: AsyncGenerator[ClientResponse[Any], None] = (
            client.stream_structured(request=request)
        )
    else:
        # Use regular streaming for unstructured requests
        stream_generator = client.stream(request=request)

    # Keep track of the last chunk for final output
    last_chunk = None

    async for chunk in stream_generator:
        content = ""
        if chunk.prompt_result and chunk.prompt_result.content_blocks:
            from electric_text.providers.functions.format_content_blocks import format_content_blocks
            content = format_content_blocks(content_blocks=chunk.prompt_result.content_blocks)
        
        is_valid = chunk.parse_result.is_valid if chunk.parse_result else False
        parsed_model = chunk.parse_result.model if chunk.parse_result else None
        
        if model_class and is_valid and parsed_model:
            formatted_model = parsed_model.model_dump_json(indent=2)
            print(f"PARTIAL RESULT (STRUCTURED): {parsed_model}\n{formatted_model}")
        else:
            # Format using provided content
            if content:
                print(f"PARTIAL RESULT (UNSTRUCTURED):\n{content}")
            else:
                print("PARTIAL RESULT (UNSTRUCTURED): [No content available]")


        # Keep the last chunk to get final content
        last_chunk = chunk

    # Process the complete content from the last chunk
    if last_chunk:
        if request.response_model is not None:
            # For structured responses, use the last chunk as the final result
            content = ""
            if last_chunk.prompt_result and last_chunk.prompt_result.content_blocks:
                from electric_text.providers.functions.format_content_blocks import format_content_blocks
                content = format_content_blocks(content_blocks=last_chunk.prompt_result.content_blocks)
            
            is_valid = last_chunk.parse_result.is_valid if last_chunk.parse_result else False
            parsed_model = last_chunk.parse_result.model if last_chunk.parse_result else None
            
            if model_class and is_valid and parsed_model:
                formatted_model = parsed_model.model_dump_json(indent=2)
                print(f"RESULT (STRUCTURED): {parsed_model}\n{formatted_model}")
            else:
                # Format using provided content
                if content:
                    print(f"RESULT (UNSTRUCTURED):\n{content}")
                else:
                    print("RESULT (UNSTRUCTURED): [No content available]")
        else:
            # For unstructured responses, extract content from content blocks
            full_content = ""
            if last_chunk.prompt_result and last_chunk.prompt_result.content_blocks:
                from electric_text.providers.functions.format_content_blocks import format_content_blocks
                full_content = format_content_blocks(content_blocks=last_chunk.prompt_result.content_blocks)


            result = f"FULL RESULT: {full_content}"

            if model_class:
                try:
                    parsed_json = json.loads(full_content)
                    result += f"\nRESULT TO JSON: {parsed_json}"
                except json.JSONDecodeError as e:
                    result += f"\nERROR PARSING JSON: {e}"
                    result += f"\nSTRUCTURED FULL RESULT: {full_content}"

            print(result)
