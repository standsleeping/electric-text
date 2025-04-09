import json


def is_complete_number(input_string: str, is_last_value: bool = False) -> bool:
    """Check if a string represents a complete number.

    Args:
        input_string: String to check
        is_last_value: Whether this value appears at the end of input

    Returns:
        True if the string is a complete number, False otherwise
    """
    # Remove whitespace
    input_string = input_string.strip()

    # Empty string is not a complete number
    if not input_string:
        return False

    # For numbers at the end of input
    if is_last_value:
        if input_string.startswith("-"):
            # For negative numbers at the end, treat as incomplete
            return False

        # For positive numbers at the end, treat as incomplete
        if input_string.replace(".", "").isdigit():
            return False

    # For other values, try parsing as JSON
    try:
        json.loads(input_string)
        return True
    except json.JSONDecodeError:
        return False
