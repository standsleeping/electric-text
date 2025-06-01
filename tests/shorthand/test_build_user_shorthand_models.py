import os
from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)


def test_empty_env(clean_env):
    """Test with no shorthand environment variables or config."""
    result = build_user_shorthand_models({})
    assert result == {}


def test_provider_shorthand_env_only(clean_env):
    """Test with provider shorthand environment variables only."""
    os.environ["ELECTRIC_TEXT_OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"
    os.environ["ELECTRIC_TEXT_ANTHROPIC_PROVIDER_NAME_SHORTHAND"] = "anthropic++ant"

    result = build_user_shorthand_models({})

    assert "oai" in result
    assert result["oai"] == ("openai", "")

    assert "ant" in result
    assert result["ant"] == ("anthropic", "")


def test_model_shorthand_env_only(clean_env):
    """Test with model shorthand environment variables only."""
    os.environ["ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_FOUR"] = "gpt-4++g4"
    os.environ["ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_FOUR_MINI"] = "gpt-4-mini++g4mini"
    os.environ["ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_CLAUDE"] = "claude-3-opus++c3"

    result = build_user_shorthand_models({})

    assert "g4" in result
    assert result["g4"] == ("openai", "gpt-4")

    assert "g4mini" in result
    assert result["g4mini"] == ("openai", "gpt-4-mini")

    assert "c3" in result
    assert result["c3"] == ("anthropic", "claude-3-opus")


def test_precedence_model_over_provider(clean_env):
    """Test that model shorthands take precedence over provider shorthands."""
    # Provider shorthand
    os.environ["ELECTRIC_TEXT_OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"

    # Model shorthand with same shorthand name
    os.environ["ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_TEST"] = "claude-3++oai"

    result = build_user_shorthand_models({})

    # The model shorthand should win
    assert "oai" in result
    assert result["oai"] == ("anthropic", "claude-3")


def test_malformed_env_entries(clean_env):
    """Test handling of malformed environment variables."""
    # Missing semicolon
    os.environ["ELECTRIC_TEXT_OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai-no-semicolon"
    os.environ["ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_TEST"] = "claude-no-semicolon"

    # Valid entries
    os.environ["ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_VALID"] = "gpt-4++g4"

    result = build_user_shorthand_models({})

    # Malformed entries should be skipped
    assert "openai-no-semicolon" not in result
    assert "claude-no-semicolon" not in result

    # Valid entries should still be processed
    assert "g4" in result
    assert result["g4"] == ("openai", "gpt-4")


def test_config_only_provider_shorthands(clean_env):
    """Test with provider shorthands from config file only."""
    config_data = {
        "provider_names": {"openai": "oai", "anthropic": "ant"},
        "models": {},
    }
    result = build_user_shorthand_models(config_data)

    assert "oai" in result
    assert result["oai"] == ("openai", "")
    assert "ant" in result
    assert result["ant"] == ("anthropic", "")


def test_config_only_model_shorthands(clean_env):
    """Test with model shorthands from config file only."""
    config_data = {
        "provider_names": {},
        "models": {
            "openai": {"gpt-4o-mini": "4o", "gpt-4": "g4"},
            "anthropic": {"claude-3-7-sonnet": "37"},
        },
    }
    result = build_user_shorthand_models(config_data)

    assert "4o" in result
    assert result["4o"] == ("openai", "gpt-4o-mini")
    assert "g4" in result
    assert result["g4"] == ("openai", "gpt-4")
    assert "37" in result
    assert result["37"] == ("anthropic", "claude-3-7-sonnet")


def test_env_overrides_config(clean_env):
    """Test that environment variables override config file values."""
    # Set environment variables with same shorthand names as config
    os.environ["ELECTRIC_TEXT_OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"
    os.environ["ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_SMALL"] = "gpt-4++4o"

    config_data = {
        "provider_names": {"openai": "oai"},
        "models": {"openai": {"gpt-4o-mini": "4o"}},
    }
    result = build_user_shorthand_models(config_data)

    # Environment values should override config values
    assert "oai" in result
    assert result["oai"] == ("openai", "")  # From env (provider shorthand)
    assert "4o" in result
    assert result["4o"] == ("openai", "gpt-4")  # From env (gpt-4, not gpt-4o-mini)

    # Should have exactly 2 entries (no duplicates)
    assert len(result) == 2


def test_mixed_env_and_config(clean_env):
    """Test combining environment variables and config file values."""
    # Set different environment variables
    os.environ["ELECTRIC_TEXT_OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"
    os.environ["ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_SMALL"] = "gpt-4o-mini++4o"

    config_data = {
        "provider_names": {"anthropic": "ant"},
        "models": {"anthropic": {"claude-3-7-sonnet": "37"}},
    }
    result = build_user_shorthand_models(config_data)

    # Should have both environment and config values
    assert "oai" in result
    assert result["oai"] == ("openai", "")
    assert "4o" in result
    assert result["4o"] == ("openai", "gpt-4o-mini")
    assert "ant" in result
    assert result["ant"] == ("anthropic", "")
    assert "37" in result
    assert result["37"] == ("anthropic", "claude-3-7-sonnet")


def test_malformed_config_entries(clean_env):
    """Test handling of malformed config entries."""
    config_data = {
        "provider_names": {
            "openai": "",  # Empty shorthand
            "anthropic": None,  # None shorthand
            "ollama": "lma",  # Valid shorthand
        },
        "models": {
            "openai": {
                "gpt-4": "",  # Empty shorthand
                "gpt-3": None,  # None shorthand
                "gpt-4o": "4o",  # Valid entry
            }
        },
    }
    result = build_user_shorthand_models(config_data)

    # Only valid entries should be processed
    assert "lma" in result
    assert result["lma"] == ("ollama", "")
    assert "4o" in result
    assert result["4o"] == ("openai", "gpt-4o")

    # Malformed entries should be skipped
    assert "" not in result
    assert len([k for k in result.keys() if k == ""]) == 0


def test_empty_config_with_env_fallback(clean_env):
    """Test with empty shorthands config structure but env vars present."""
    os.environ["ELECTRIC_TEXT_OPENAI_PROVIDER_NAME_SHORTHAND"] = "openai++oai"

    config_data = {}
    result = build_user_shorthand_models(config_data)

    # Should still work with environment variables
    assert "oai" in result
    assert result["oai"] == ("openai", "")
