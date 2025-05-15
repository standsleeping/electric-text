import tempfile
from textwrap import dedent
from unittest.mock import patch

from electric_text.configuration.functions.get_cached_config import get_cached_config


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
            "electric_text.configuration.functions.get_cached_config.load_config"
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
