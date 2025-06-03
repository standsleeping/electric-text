from pathlib import Path
from textwrap import dedent

from electric_text.configuration.functions.get_cached_config import get_cached_config
from electric_text.configuration.data.config import Config
from tests.boundaries import mock_filesystem, MockFileSystem, MockFile


def test_get_cached_config() -> None:
    """Caches configuration and returns same object on subsequent calls."""
    # Create test config file
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                dedent("""
                logging:
                  level: "DEBUG"
                provider_defaults:
                  default_model: "test:model"
                """).strip(),
            )
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config_path = str(temp_dir / "config.yaml")

        # Clear cache before test
        get_cached_config.cache_clear()

        # Call get_cached_config multiple times with the same path
        config1 = get_cached_config(config_path)
        config2 = get_cached_config(config_path)
        config3 = get_cached_config(config_path)

        # Verify the configs are the same object (cached)
        assert config1 is config2
        assert config2 is config3

        # Verify the config content is correct
        assert isinstance(config1, Config)
        assert config1.logging == {"level": "DEBUG"}
        assert config1.provider_defaults == {"default_model": "test:model"}


def test_get_cached_config_different_paths() -> None:
    """Cache is keyed by path, but with maxsize=1 only last path is cached."""
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config1.yaml"),
                dedent("""
                logging:
                  level: "INFO"
                """).strip(),
            ),
            MockFile(
                Path("config2.yaml"),
                dedent("""
                logging:
                  level: "ERROR"
                """).strip(),
            ),
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config1_path = str(temp_dir / "config1.yaml")
        config2_path = str(temp_dir / "config2.yaml")

        # Clear cache before test
        get_cached_config.cache_clear()

        # Get configs from different paths
        config1 = get_cached_config(config1_path)
        config2 = get_cached_config(config2_path)

        # Verify content is different
        assert config1.logging == {"level": "INFO"}
        assert config2.logging == {"level": "ERROR"}

        # With maxsize=1, calling with config2_path evicted config1 from cache
        # So calling config2_path again should return the cached object
        config2_again = get_cached_config(config2_path)
        assert config2 is config2_again

        # But calling config1_path again will create a new object (not cached)
        config1_again = get_cached_config(config1_path)
        assert config1 is not config1_again  # Different objects due to cache eviction
        assert config1_again.logging == {"level": "INFO"}  # But same content
