import pytest
from tempfile import TemporaryDirectory
from pathlib import Path

from electric_text.prompting.functions.get_prompt_directory import get_prompt_directory


def test_electric_text_prompt_directory_env_var_takes_precedence(monkeypatch, clean_env, config_with_prompt_directory):
    """Uses ELECTRIC_TEXT_PROMPT_DIRECTORY environment variable when set."""
    
    with TemporaryDirectory() as temp_dir:
        # Set environment variable
        monkeypatch.setenv("ELECTRIC_TEXT_PROMPT_DIRECTORY", temp_dir)
        
        # Get prompt directory - should use env var
        result = get_prompt_directory()
        
        assert result == temp_dir


def test_prompts_directory_from_config(clean_env, config_with_prompt_directory):
    """Uses prompts.directory from config file when env var not set."""
    
    # Get prompt directory - should use config value
    result = get_prompt_directory()
    
    assert result == "/custom/prompt/path"


def test_no_prompt_directory_configured(clean_env, monkeypatch):
    """Raises ValueError when neither env var nor config is set."""
    
    # Mock get_cached_config to raise an exception (simulating no config file)
    def mock_config():
        raise Exception("No config file found")
    
    monkeypatch.setattr(
        "electric_text.prompting.functions.get_prompt_directory.get_cached_config",
        mock_config
    )
    
    with pytest.raises(ValueError, match="ELECTRIC_TEXT_PROMPT_DIRECTORY environment variable is not set and prompts.directory is not configured"):
        get_prompt_directory()