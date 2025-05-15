import tempfile
from textwrap import dedent
from unittest.mock import patch
from electric_text.configuration.functions.get_config_value import (
    get_config_value,
    get_cached_config,
)


def test_get_config_value_simple_path() -> None:
    """Gets a value from a simple configuration path."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            logging:
              level: "DEBUG"
            """).strip()
        )
        temp_file.flush()

        # Get the value from the config
        value = get_config_value("logging.level", config_path=temp_file.name)

        # Verify the value is correct
        assert value == "DEBUG"


def test_get_config_value_nested_path() -> None:
    """Gets a value from a nested configuration path."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            provider_defaults:
              timeout:
                default_seconds: 30
            """).strip()
        )
        temp_file.flush()

        # Get the value from the config
        value = get_config_value(
            "provider_defaults.timeout.default_seconds", config_path=temp_file.name
        )

        # Verify the value is correct
        assert value == 30


def test_get_config_value_with_default() -> None:
    """Returns the default value when the path is not found."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            logging:
              level: "DEBUG"
            """).strip()
        )
        temp_file.flush()

        # Get a value that does not exist
        value = get_config_value(
            "nonexistent.path", default="default_value", config_path=temp_file.name
        )

        # Verify the default value is returned
        assert value == "default_value"


def test_get_config_value_invalid_path() -> None:
    """Returns the default value when the path is invalid."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            logging:
              level: "DEBUG"
            """).strip()
        )
        temp_file.flush()

        # Try to access a non-dict value as if it were a dict
        value = get_config_value(
            "logging.level.invalid", default="default_value", config_path=temp_file.name
        )

        # Verify the default value is returned
        assert value == "default_value"


def test_get_cached_config() -> None:
    """Only loads the configuration once when using get_cached_config."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            logging:
              level: "DEBUG"
            """).strip()
        )
        temp_file.flush()

        # Using patch to count how many times load_config is called
        with patch(
            "electric_text.configuration.functions.get_config_value.load_config"
        ) as mock_load_config:
            # Set up the mock to return a valid config
            mock_load_config.return_value = get_cached_config(temp_file.name)

            # Call get_cached_config multiple times with the same path
            config1 = get_cached_config(temp_file.name)
            config2 = get_cached_config(temp_file.name)
            config3 = get_cached_config(temp_file.name)

            # Verify load_config was only called once
            assert mock_load_config.call_count == 1

            # Verify the configs are the same object (cached)
            assert config1 is config2
            assert config2 is config3
