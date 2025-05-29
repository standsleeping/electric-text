import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from electric_text.prompting.functions.get_prompt_list import get_prompt_list


@pytest.mark.asyncio
async def test_electric_text_prompt_directory_env_var(monkeypatch):
    """Loads prompt list from ELECTRIC_TEXT_PROMPT_DIRECTORY environment variable path."""

    # Create temporary directory with a test prompt config
    with TemporaryDirectory() as temp_dir:
        # Create a test prompt config file
        config_data = {
            "name": "test_prompt",
            "description": "Test prompt for env var testing",
            "system_message_path": "test_system.txt",
        }

        config_path = Path(temp_dir) / "test_prompt.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Create the system message file
        system_path = Path(temp_dir) / "test_system.txt"
        with open(system_path, "w") as f:
            f.write("Test system message")

        # Set environment variable
        monkeypatch.setenv("ELECTRIC_TEXT_PROMPT_DIRECTORY", temp_dir)

        # Get prompt list - should use env var directory
        prompt_configs = get_prompt_list()

        # Verify prompt loaded from specified directory
        assert len(prompt_configs) == 1
        assert prompt_configs[0].name == "test_prompt"
