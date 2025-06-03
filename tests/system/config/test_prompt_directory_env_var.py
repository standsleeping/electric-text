import pytest
from pathlib import Path

from electric_text.prompting.functions.get_prompt_list import get_prompt_list
from tests.boundaries import mock_filesystem, mock_env, MockFileSystem, MockFile


@pytest.mark.asyncio
async def test_electric_text_prompt_directory_env_var():
    """Loads prompt list from ELECTRIC_TEXT_PROMPT_DIRECTORY environment variable path."""

    # Create test file structure
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("test_prompt.json"),
                {
                    "name": "test_prompt",
                    "description": "Test prompt for env var testing",
                    "system_message_path": "test_system.txt",
                },
                is_json=True,
            ),
            MockFile(
                Path("test_system.txt"),
                "Test system message",
            ),
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        # Set environment variable
        with mock_env({"ELECTRIC_TEXT_PROMPT_DIRECTORY": str(temp_dir)}):
            # Get prompt list - should use env var directory
            prompt_configs = get_prompt_list()

            # Verify prompt loaded from specified directory
            assert len(prompt_configs) == 1
            assert prompt_configs[0].name == "test_prompt"
