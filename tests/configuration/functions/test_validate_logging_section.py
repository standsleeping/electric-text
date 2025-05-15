from electric_text.configuration.functions.validate_logging_section import validate_logging_section


def test_validate_logging_section_valid() -> None:
    """Returns no issues for valid logging configuration."""
    logging_config = {"level": "DEBUG"}
    issues = validate_logging_section(logging_config)
    assert issues == []


def test_validate_logging_section_invalid_level() -> None:
    """Returns issues for invalid log level."""
    logging_config = {"level": "TRACE"}
    issues = validate_logging_section(logging_config)
    assert len(issues) == 1
    assert "Invalid log level" in issues[0]
    assert "TRACE" in issues[0]


def test_validate_logging_section_missing_level() -> None:
    """Returns no issues when log level is missing (it's optional)."""
    logging_config = {"other_setting": "value"}
    issues = validate_logging_section(logging_config)
    assert issues == []