import os
import pytest
from electric_text.app.functions.parse_provider_model import parse_provider_model


def test_parse_provider_model_basic():
    """Test basic model string parsing."""
    model_string = "openai:gpt-4"
    provider, model = parse_provider_model(model_string)

    assert provider == "openai"
    assert model == "gpt-4"


def test_parse_provider_model_with_colon():
    """Test parsing when model name contains colons."""
    model_string = "anthropic:claude-3:sonnet"
    provider, model = parse_provider_model(model_string)

    assert provider == "anthropic"
    assert model == "claude-3:sonnet"


def test_parse_provider_model_provider_shorthand(clean_env):
    """Test parsing a provider shorthand."""
    # Set up environment variables
    os.environ["OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"

    # Test shorthand parsing
    provider, model = parse_provider_model("oai")

    assert provider == "openai"
    assert model == ""


def test_parse_provider_model_model_shorthand(clean_env):
    """Test parsing a model shorthand."""
    # Set up environment variables
    os.environ["OPENAI_MODEL_SHORTHAND_FOUR"] = "gpt-4++g4"

    # Test shorthand parsing
    provider, model = parse_provider_model("g4")

    assert provider == "openai"
    assert model == "gpt-4"


def test_parse_provider_model_no_matching_shorthand(clean_env):
    """Test error when no matching shorthand is found."""
    with pytest.raises(ValueError):
        parse_provider_model("unknown_shorthand")


def test_parse_provider_model_precedence(clean_env):
    """Test precedence between standard format and shorthand."""
    # Set up a shorthand that looks like a standard format
    os.environ["OPENAI_MODEL_SHORTHAND_TEST"] = "gpt-5;openai:gpt-4"

    # Even though "openai:gpt-4" looks like a standard format,
    # it should be parsed as a shorthand
    provider, model = parse_provider_model("openai:gpt-4")

    # Standard format parser should be used first
    assert provider == "openai"
    assert model == "gpt-4"
