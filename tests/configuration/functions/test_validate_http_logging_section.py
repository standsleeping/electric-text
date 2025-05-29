from electric_text.configuration.functions.validate_http_logging_section import (
    validate_http_logging_section,
)


def test_valid_http_logging_config():
    """Valid HTTP logging config has no issues"""
    config = {"enabled": True, "log_dir": "/path/to/logs"}
    issues = validate_http_logging_section(config)
    assert issues == []


def test_valid_http_logging_config_with_false():
    """Valid HTTP logging config with enabled=False has no issues"""
    config = {"enabled": False, "log_dir": "./logs"}
    issues = validate_http_logging_section(config)
    assert issues == []


def test_empty_http_logging_config():
    """Empty HTTP logging config has no issues"""
    config = {}
    issues = validate_http_logging_section(config)
    assert issues == []


def test_invalid_enabled_type():
    """Invalid enabled type returns issue"""
    config = {"enabled": "true"}
    issues = validate_http_logging_section(config)
    assert "http_logging.enabled must be a boolean" in issues


def test_invalid_log_dir_type():
    """Invalid log_dir type returns issue"""
    config = {"log_dir": 123}
    issues = validate_http_logging_section(config)
    assert "http_logging.log_dir must be a string" in issues


def test_multiple_invalid_fields():
    """Multiple invalid fields return multiple issues"""
    config = {"enabled": "yes", "log_dir": ["invalid"]}
    issues = validate_http_logging_section(config)
    assert len(issues) == 2
    assert "http_logging.enabled must be a boolean" in issues
    assert "http_logging.log_dir must be a string" in issues
