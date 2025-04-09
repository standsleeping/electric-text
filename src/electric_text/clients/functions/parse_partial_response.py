import json
from typing import Dict, Any, List

from electric_text.clients.functions.is_complete_number import is_complete_number


def parse_partial_response(partial_response: str) -> Dict[str, Any]:
    """Parse a partial JSON response and return as much structured information as possible.

    Args:
        partial_response: A potentially incomplete JSON string

    Returns:
        A dictionary containing the parsed information from the partial JSON

    Example:
        '{ "hi": "th' -> {'hi': None}  # Incomplete value
        '{ "hi":' -> {'hi': None}      # Missing value
        '{ "hi": "hello"' -> {'hi': 'hello'}  # Missing closing brace
    """
    # First, try parsing as complete JSON
    try:
        parsed: Dict[str, Any] = json.loads(partial_response)
        return parsed
    except json.JSONDecodeError:
        pass

    # Handle partial JSON
    result: Dict[str, Any] = {}

    # Remove whitespace
    cleaned = partial_response.strip()

    # Should at least start with {
    if not cleaned.startswith("{"):
        return result

    # Remove outer braces if they exist
    content = cleaned.strip("{}").strip()

    # Track quote and brace balance for complex value parsing
    in_string = False
    brace_count = 0
    bracket_count = 0
    current_pair: List[str] = []
    current_char_list: List[str] = []

    # Process character by character to handle nested structures
    for char in content:
        if char == '"' and (not current_char_list or current_char_list[-1] != "\\"):
            in_string = not in_string

        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
            elif char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1

        if char == "," and not in_string and brace_count == 0 and bracket_count == 0:
            # End of a complete pair
            if current_char_list:
                current_pair.append("".join(current_char_list).strip())
                current_char_list = []
                if len(current_pair) == 2:
                    try:
                        key = json.loads(current_pair[0])
                        value_str = current_pair[1].strip()
                        try:
                            # Only parse numbers if complete
                            if value_str.lstrip("-").replace(".", "").isdigit():
                                if is_complete_number(value_str, is_last_value=False):
                                    value = json.loads(value_str)
                                else:
                                    value = None
                            else:
                                value = json.loads(value_str)
                            result[key] = value
                        except json.JSONDecodeError:
                            result[key] = None
                    except json.JSONDecodeError:
                        pass
                current_pair = []
        elif char == ":" and not in_string and brace_count == 0 and bracket_count == 0:
            # End of key
            if current_char_list:
                current_pair.append("".join(current_char_list).strip())
                current_char_list = []
        else:
            current_char_list.append(char)

    # Handle the last pair
    if current_char_list:
        current_pair.append("".join(current_char_list).strip())
    if len(current_pair) > 0:
        try:
            key = json.loads(current_pair[0])
            value = None
            if len(current_pair) > 1:
                value_str = current_pair[1].strip()
                try:
                    # Only parse numbers if complete
                    if value_str.lstrip("-").replace(".", "").isdigit():
                        if is_complete_number(value_str, is_last_value=True):
                            value = json.loads(value_str)
                    else:
                        value = json.loads(value_str)
                except json.JSONDecodeError:
                    pass
            result[key] = value
        except json.JSONDecodeError:
            pass

    return result
