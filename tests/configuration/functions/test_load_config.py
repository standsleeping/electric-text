import os
import tempfile
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from electric_text.configuration.functions.load_config import load_config
from electric_text.configuration.data.config import Config


def test_load_config_from_explicit_path() -> None:
    """Loads configuration from explicitly provided path."""
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            provider_defaults:
              default_model: "ollama:llama3.1:8b"
            logging:
              level: "DEBUG"
            """).strip()
        )
        temp_file.flush()

        # Load the config from the temp file
        config = load_config(temp_file.name)

        # Verify the config was loaded correctly
        assert isinstance(config, Config)
        assert config.provider_defaults == {"default_model": "ollama:llama3.1:8b"}
        assert config.logging == {"level": "DEBUG"}


def test_load_config_from_environment_variable() -> None:
    """Loads configuration from ELECTRIC_TEXT_CONFIG environment variable."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            logging:
              level: "INFO"
            """).strip()
        )
        temp_file.flush()

        # Set the environment variable to point to our temp file
        with patch.dict(os.environ, {"ELECTRIC_TEXT_CONFIG": temp_file.name}):
            config = load_config()

            # Verify the config was loaded correctly
            assert isinstance(config, Config)
            assert config.logging == {"level": "INFO"}


def test_load_config_from_default_locations() -> None:
    """Loads configuration from default locations in order of precedence."""
    # Create a temporary file that will be used as ./config.yaml
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            provider_defaults:
              default_model: "ollama:llama3.1:8b"
            """).strip()
        )
        temp_file.flush()

        # Patch the expanduser method to return our mock paths
        with patch("pathlib.Path.expanduser", return_value=Path(temp_file.name)):
            # Patch the DEFAULT_LOCATIONS constant
            with patch(
                "electric_text.configuration.functions.load_config.DEFAULT_LOCATIONS",
                [temp_file.name],
            ):
                config = load_config()

                # Verify the config was loaded correctly
                assert isinstance(config, Config)
                assert config.provider_defaults == {
                    "default_model": "ollama:llama3.1:8b"
                }


def test_load_config_empty_file() -> None:
    """Returns empty config when file is empty."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write("")
        temp_file.flush()

        config = load_config(temp_file.name)

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
