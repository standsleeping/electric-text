import pytest

from electric_text.shorthand.functions.build_user_shorthand_models import (
    build_user_shorthand_models,
)
from tests.boundaries import mock_env


@pytest.mark.asyncio
async def test_electric_text_provider_shorthand_env_var():
    """Builds shorthand models from ELECTRIC_TEXT_{PROVIDER}_PROVIDER_NAME_SHORTHAND."""

    # Set environment variables for provider and model shorthand
    with mock_env(
        {
            "ELECTRIC_TEXT_ANTHROPIC_PROVIDER_NAME_SHORTHAND": "anthropic++test-provider",
            "ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_TEST": "claude-3-sonnet++test-model",
        }
    ):
        # Build shorthand models
        shorthand_models = build_user_shorthand_models({})

        # Verify the model shorthand works (which requires the provider shorthand to work)
        assert "test-model" in shorthand_models
        assert shorthand_models["test-model"] == ("anthropic", "claude-3-sonnet")
