import os
import pytest


@pytest.fixture
def clean_env():
    """Fixture to save and restore environment variables."""
    # Save current environment
    env_backup = os.environ.copy()

    # Clear relevant environment variables
    for key in list(os.environ.keys()):
        if "_PROVIDER_NAME_SHORTHAND" in key or "_MODEL_SHORTHAND_" in key:
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(env_backup)
