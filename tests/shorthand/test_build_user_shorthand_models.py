import os
from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)


def test_empty_env(clean_env):
    """Test with no shorthand environment variables."""
    result = build_user_shorthand_models()
    assert result == {}


def test_provider_shorthand(clean_env):
    """Test with provider shorthand environment variables."""
    os.environ["OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"
    os.environ["ANTHROPIC_PROVIDER_NAME_SHORTHAND"] = "anthropic++ant"

    result = build_user_shorthand_models()

    assert "oai" in result
    assert result["oai"] == ("openai", "")

    assert "ant" in result
    assert result["ant"] == ("anthropic", "")


def test_model_shorthand(clean_env):
    """Test with model shorthand environment variables."""
    os.environ["OPENAI_MODEL_SHORTHAND_FOUR"] = "gpt-4++g4"
    os.environ["OPENAI_MODEL_SHORTHAND_FOUR_MINI"] = "gpt-4-mini++g4mini"
    os.environ["ANTHROPIC_MODEL_SHORTHAND_CLAUDE"] = "claude-3-opus++c3"

    result = build_user_shorthand_models()

    assert "g4" in result
    assert result["g4"] == ("openai", "gpt-4")

    assert "g4mini" in result
    assert result["g4mini"] == ("openai", "gpt-4-mini")

    assert "c3" in result
    assert result["c3"] == ("anthropic", "claude-3-opus")


def test_precedence(clean_env):
    """Test that model shorthands take precedence over provider shorthands."""
    # Provider shorthand
    os.environ["OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"

    # Model shorthand with same shorthand name
    os.environ["ANTHROPIC_MODEL_SHORTHAND_TEST"] = "claude-3++oai"

    result = build_user_shorthand_models()

    # The model shorthand should win
    assert "oai" in result
    assert result["oai"] == ("anthropic", "claude-3")


def test_malformed_entries(clean_env):
    """Test handling of malformed environment variables."""
    # Missing semicolon
    os.environ["OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai-no-semicolon"
    os.environ["ANTHROPIC_MODEL_SHORTHAND_TEST"] = "claude-no-semicolon"

    # Valid entries
    os.environ["OPENAI_MODEL_SHORTHAND_VALID"] = "gpt-4++g4"

    result = build_user_shorthand_models()

    # Malformed entries should be skipped
    assert "openai-no-semicolon" not in result
    assert "claude-no-semicolon" not in result

    # Valid entries should still be processed
    assert "g4" in result
    assert result["g4"] == ("openai", "gpt-4")
