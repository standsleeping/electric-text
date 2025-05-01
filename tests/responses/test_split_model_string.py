import pytest
from electric_text.responses.split_model_string import split_model_string


def test_basic_splitting():
    """Test basic model string splitting."""
    model_string = "openai:gpt-4"
    provider, model = split_model_string(model_string)

    assert provider == "openai"
    assert model == "gpt-4"


def test_model_with_colon():
    """Test splitting when model name contains colons."""
    model_string = "anthropic:claude-3:sonnet"
    provider, model = split_model_string(model_string)

    assert provider == "anthropic"
    assert model == "claude-3:sonnet"


def test_empty_model():
    """Test splitting when model name is empty."""
    model_string = "openai:"
    provider, model = split_model_string(model_string)

    assert provider == "openai"
    assert model == ""


def test_no_colon():
    """Test error handling when string has no colon."""
    with pytest.raises(ValueError):
        split_model_string("gpt4")
