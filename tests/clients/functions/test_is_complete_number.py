from electric_text.clients import is_complete_number


def test_is_complete_number_empty_string():
    """Test that empty string is not a complete number."""
    assert is_complete_number("") is False
    assert is_complete_number("   ") is False


def test_is_complete_number_integer():
    """Test integer values."""
    # Regular integers
    assert is_complete_number("42") is True
    assert is_complete_number("-42") is True

    # With whitespace
    assert is_complete_number("  42  ") is True
    assert is_complete_number("  -42  ") is True


def test_is_complete_number_float():
    """Test floating point values."""
    # Regular floats
    assert is_complete_number("3.14") is True
    assert is_complete_number("-3.14") is True

    # With whitespace
    assert is_complete_number("  3.14  ") is True
    assert is_complete_number("  -3.14  ") is True


def test_is_complete_number_non_numeric():
    """Test non-numeric values."""
    assert is_complete_number("text") is False
    assert is_complete_number("42text") is False
    assert is_complete_number("[1,2,3]") is True  # Valid JSON
    assert is_complete_number("null") is True  # Valid JSON
    assert is_complete_number("true") is True  # Valid JSON
    assert is_complete_number("false") is True  # Valid JSON


def test_is_complete_number_at_end_of_input():
    """Test behavior when is_last_value is True."""
    # Numbers at the end of input are treated as incomplete
    assert is_complete_number("42", is_last_value=True) is False
    assert is_complete_number("3.14", is_last_value=True) is False

    # Negative numbers at the end are always incomplete
    assert is_complete_number("-42", is_last_value=True) is False
    assert is_complete_number("-3.14", is_last_value=True) is False

    # Non-numeric values don't have this special treatment
    assert is_complete_number("true", is_last_value=True) is True
    assert is_complete_number("null", is_last_value=True) is True
