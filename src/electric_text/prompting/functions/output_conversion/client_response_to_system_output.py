from electric_text.clients.data.validation_model import ValidationModel

from electric_text.clients.data.client_response import ClientResponse
from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.data.system_output_type import SystemOutputType
from electric_text.prompting.data.text_output import TextOutput
from electric_text.prompting.data.data_output import DataOutput
from electric_text.prompting.data.tool_call_output import ToolCallOutput


def client_response_to_system_output[OutputSchema: ValidationModel](
    response: ClientResponse[OutputSchema],
) -> SystemOutput:
    """Convert ClientResponse to SystemOutput for JSON serialization.

    Args:
        response: The ClientResponse to convert

    Returns:
        SystemOutput with appropriate response type and data
    """

    # Check if we have tool calls
    if response.has_tool_calls:
        tool_call = response.first_tool_call
        if tool_call:
            name, inputs = tool_call
            return SystemOutput(
                response_type=SystemOutputType.TOOL_CALL,
                tool_call=ToolCallOutput(
                    name=name,
                    inputs=inputs,
                ),
            )

    # Check if we have structured data
    if response.validated_output is not None:
        # This validated_modelcould be None!
        # See history_to_client_response.py calling create_parse_result.py for more details.
        validated_model: OutputSchema | None = response.validated_output
        if validated_model is not None:
            return SystemOutput(
                response_type=SystemOutputType.DATA,
                data=DataOutput(
                    data=validated_model.model_dump(),
                    is_valid=True,
                    schema_name=validated_model.__class__.__name__,
                ),
            )

    # Check if we have parsed content but validation failed
    if response.parsed_content is not None:
        validation_error_msg = None
        if response.validation_error:
            validation_error_msg = str(response.validation_error)
        elif response.json_error:
            validation_error_msg = str(response.json_error)

        return SystemOutput(
            response_type=SystemOutputType.DATA,
            data=DataOutput(
                data=response.parsed_content or {},
                is_valid=False,
                validation_error=validation_error_msg,
            ),
        )

    # Default to text output
    text_content = response.text_content
    return SystemOutput(
        response_type=SystemOutputType.TEXT,
        text=TextOutput(content=text_content),
    )
