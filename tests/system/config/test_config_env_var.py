import pytest
from pathlib import Path

from electric_text.configuration.functions.load_config import load_config
from tests.boundaries import mock_filesystem, mock_env, MockFileSystem, MockFile


@pytest.mark.asyncio
async def test_electric_text_config_env_var():
    """Loads configuration from ELECTRIC_TEXT_CONFIG environment variable path."""

    # Create test config file
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                {"prompts": {"directory": "/custom/prompts"}},
                is_json=True,
            )
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config_path = str(temp_dir / "config.yaml")

        # Set environment variable
        with mock_env({"ELECTRIC_TEXT_CONFIG": config_path}):
            # Load config - should use env var path
            config = load_config()

            # Verify config loaded from specified path
            assert config.raw_config["prompts"]["directory"] == "/custom/prompts"
