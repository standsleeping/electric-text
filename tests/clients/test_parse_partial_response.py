from electric_text.clients import parse_partial_response


def test_complete_json():
    """Parses complete valid JSON."""
    input_json = '{"name": "test", "value": 42}'
    result = parse_partial_response(input_json)
    assert result == {"name": "test", "value": 42}


def test_partial_json_incomplete_value():
    """Parses JSON with incomplete value."""
    input_json = '{"name": "te'
    result = parse_partial_response(input_json)
    assert result == {"name": None}


def test_partial_json_missing_value():
    """Parses JSON with missing value."""
    input_json = '{"name":'
    result = parse_partial_response(input_json)
    assert result == {"name": None}


def test_partial_json_multiple_pairs():
    """Parses JSON with multiple key-value pairs, some complete and some incomplete."""
    input_json = '{"name": "test", "value": 42, "description": "par'
    result = parse_partial_response(input_json)
    assert result == {"name": "test", "value": 42, "description": None}


def test_partial_json_incomplete_key():
    """Parses JSON with incomplete key."""
    input_json = '{"nam'
    result = parse_partial_response(input_json)
    assert result == {}


def test_partial_json_nested_object():
    """Parses JSON with a complete nested object."""
    input_json = '{"name": "Ryan", "deets": {"age": 37, "city": "Omaha"}, "status": "ac'
    result = parse_partial_response(input_json)
    assert result == {
        "name": "Ryan",
        "deets": {"age": 37, "city": "Omaha"},
        "status": None,
    }


def test_empty_input():
    """Parses empty string."""
    result = parse_partial_response("")
    assert result == {}


def test_invalid_json():
    """Parses invalid JSON."""
    result = parse_partial_response("not json at all")
    assert result == {}


def test_partial_json_array_value():
    """Parses JSON with a complete array value."""
    input_json = '{"name": "test", "numbers": [1, 2, 3], "tags": ["a", "b'
    result = parse_partial_response(input_json)
    assert result == {"name": "test", "numbers": [1, 2, 3], "tags": None}


def test_partial_json_boolean_value():
    """Parses JSON with boolean values."""
    input_json = '{"name": "test", "active": true, "verified": fal'
    result = parse_partial_response(input_json)
    assert result == {"name": "test", "active": True, "verified": None}


def test_partial_json_null_value():
    """Parses JSON with null value."""
    input_json = '{"name": "test", "value": null, "status": nul'
    result = parse_partial_response(input_json)
    assert result == {"name": "test", "value": None, "status": None}


def test_partial_json_number_value():
    """Parses JSON with number values."""
    input_json = '{"integer": 42, "float": 3.14, "negative": -1'
    result = parse_partial_response(input_json)
    assert result == {"integer": 42, "float": 3.14, "negative": None}
