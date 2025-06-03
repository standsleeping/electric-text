from pathlib import Path
from textwrap import dedent

from electric_text.configuration.functions.load_config import load_config
from electric_text.configuration.data.config import Config
from tests.boundaries import (
    mock_filesystem,
    mock_env,
    mock_boundaries,
    MockFileSystem,
    MockFile,
)


def test_load_config_from_explicit_path() -> None:
    """Loads configuration from explicitly provided path."""
    # Create a temporary YAML file
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                dedent("""
                provider_defaults:
                  default_model: "ollama:llama3.1:8b"
                logging:
                  level: "DEBUG"
                """).strip(),
            )
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config_path = temp_dir / "config.yaml"

        # Load the config from the temp file
        config = load_config(str(config_path))

        # Verify the config was loaded correctly
        assert isinstance(config, Config)
        assert config.provider_defaults == {"default_model": "ollama:llama3.1:8b"}
        assert config.logging == {"level": "DEBUG"}


def test_load_config_from_environment_variable() -> None:
    """Loads configuration from ELECTRIC_TEXT_CONFIG environment variable."""
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                dedent("""
                logging:
                  level: "INFO"
                """).strip(),
            )
        ]
    )

    with mock_boundaries(filesystem=file_structure, env_vars={}) as (_, temp_dir):
        config_path = temp_dir / "config.yaml"

        # Set the environment variable to point to our temp file
        with mock_env({"ELECTRIC_TEXT_CONFIG": str(config_path)}):
            config = load_config()

            # Verify the config was loaded correctly
            assert isinstance(config, Config)
            assert config.logging == {"level": "INFO"}


def test_load_config_from_default_locations() -> None:
    """Loads configuration from default locations in order of precedence."""
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                dedent("""
                provider_defaults:
                  default_model: "ollama:llama3.1:8b"
                """).strip(),
            )
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config_path = str(temp_dir / "config.yaml")

        config = load_config(search_locations=[config_path])

        # Verify the config was loaded correctly
        assert isinstance(config, Config)
        assert config.provider_defaults == {"default_model": "ollama:llama3.1:8b"}


def test_load_config_empty_file() -> None:
    """Returns empty config when file is empty."""
    file_structure = MockFileSystem([MockFile(Path("empty_config.yaml"), "")])

    with mock_filesystem(file_structure) as temp_dir:
        config_path = temp_dir / "empty_config.yaml"

        config = load_config(str(config_path))

        # Verify default values are used
        assert isinstance(config, Config)
        assert config.provider_defaults == {}
        assert config.tool_boxes == {}
        assert config.logging == {"level": "ERROR"}


def test_load_config_nonexistent_file() -> None:
    """Raises error when explicit file path does not exist."""
    # Use a nonexistent file path
    try:
        load_config("/nonexistent/path/to/config.yaml")
        assert False, "Expected FileNotFoundError to be raised"
    except FileNotFoundError as e:
        assert "Config file not found" in str(e)
