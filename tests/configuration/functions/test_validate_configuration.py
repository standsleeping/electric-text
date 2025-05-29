from electric_text.configuration.data.config import Config
from electric_text.configuration.functions.validate_configuration import validate_configuration


def test_validate_configuration_valid() -> None:
    """Returns no issues for valid configuration."""
    config = Config(
        provider_defaults={"default_model": "ollama:llama3.1:8b"},
        tool_boxes={"default": ["tool1", "tool2"]},
        logging={"level": "INFO"},
        http_logging={"enabled": True, "log_dir": "./logs"},
        raw_config={},
    )
    
    issues = validate_configuration(config)
    assert issues == []


def test_validate_configuration_missing_required_section() -> None:
    """Returns issues for missing required sections."""
    config = Config(
        provider_defaults={},  # Empty provider_defaults
        tool_boxes={"default": ["tool1", "tool2"]},
        logging={},
        http_logging={},
        raw_config={},
    )
    
    issues = validate_configuration(config)
    assert len(issues) >= 1
    # The issue should mention missing default_model
    assert any("default_model" in issue for issue in issues)


def test_validate_configuration_multiple_issues() -> None:
    """Validates configuration and returns multiple issues."""
    config = Config(
        provider_defaults={"some_setting": "value"},  # Missing default_model
        tool_boxes={"default": "not_a_list"},  # Not a list
        logging={"level": "INVALID"},  # Invalid log level
        http_logging={},
        raw_config={},
    )
    
    issues = validate_configuration(config)
    
    assert len(issues) >= 3
    assert any("default_model" in issue for issue in issues)
    assert any("Invalid log level" in issue for issue in issues)
    assert any("Invalid tools list" in issue for issue in issues)