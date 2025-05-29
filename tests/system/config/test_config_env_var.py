import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile

from electric_text.configuration.functions.load_config import load_config


@pytest.mark.asyncio
async def test_electric_text_config_env_var(monkeypatch):
    """Loads configuration from ELECTRIC_TEXT_CONFIG environment variable path."""

    # Create temporary config file
    with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_data = {"prompts": {"directory": "/custom/prompts"}}
        yaml.dump(config_data, f)
        temp_config_path = f.name

    try:
        # Set environment variable
        monkeypatch.setenv("ELECTRIC_TEXT_CONFIG", temp_config_path)

        # Load config - should use env var path
        config = load_config()

        # Verify config loaded from specified path
        assert config.raw_config["prompts"]["directory"] == "/custom/prompts"

    finally:
        # Clean up
        Path(temp_config_path).unlink()
