from electric_text.logging import get_logger


def test_get_logger_with_name() -> None:
    """Uses an explicit name."""
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"


def test_get_logger_fallback() -> None:
    """Uses fallback name when no name is provided."""
    logger = get_logger()
    assert logger.name == "electric_text"
