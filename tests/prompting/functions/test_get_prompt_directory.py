import pytest
from pathlib import Path

from electric_text.prompting.functions.get_prompt_directory import (
    get_prompt_directory,
    PROMPT_DIR_NOT_CONFIGURED_MSG,
)
from tests.boundaries import mock_env, mock_filesystem, MockFileSystem, MockFile


def test_no_prompt_directory_configured(clean_env):
    """Raises ValueError when neither env var nor config is set."""

    # Create an empty config file that doesn't have prompts.directory
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                {
                    "logging": {"level": "INFO"}
                    # No prompts.directory section
                },
                is_json=True,
            )
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config_path = str(temp_dir / "config.yaml")

        # Clear environment and set config path without prompts directory
        with mock_env(
            {"ELECTRIC_TEXT_CONFIG": config_path},
            clear_prefix="ELECTRIC_TEXT_",
        ):
            with pytest.raises(
                ValueError,
                match=PROMPT_DIR_NOT_CONFIGURED_MSG,
            ):
                get_prompt_directory()
