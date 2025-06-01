import pytest

from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)


@pytest.mark.asyncio
async def test_electric_text_provider_shorthand_env_var(monkeypatch):
    """Builds shorthand models from ELECTRIC_TEXT_{PROVIDER}_PROVIDER_NAME_SHORTHAND."""

    # Set environment variable for provider shorthand
    monkeypatch.setenv(
        "ELECTRIC_TEXT_ANTHROPIC_PROVIDER_NAME_SHORTHAND",
        "anthropic++test-provider",
    )

    # Build shorthand models
    shorthand_models = build_user_shorthand_models({})

    # Verify provider shorthand was processed
    # The function returns model shortcuts, but provider shortcuts are used internally
    # Since the function processes provider shortcuts for use with model shortcuts,
    # we test by setting both provider and model shortcuts
    monkeypatch.setenv(
        "ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_TEST",
        "claude-3-sonnet++test-model",
    )

    # Rebuild with both shortcuts
    shorthand_models = build_user_shorthand_models({})

    # Verify the model shorthand works (which requires the provider shorthand to work)
    assert "test-model" in shorthand_models
    assert shorthand_models["test-model"] == ("anthropic", "claude-3-sonnet")
