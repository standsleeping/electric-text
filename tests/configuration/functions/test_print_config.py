import io
import tempfile
from textwrap import dedent

from electric_text.configuration.functions.print_config import print_config


def test_print_config_valid_file() -> None:
    """Prints a valid configuration file."""
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            provider_defaults:
              default_model: "ollama:llama3.1:8b"
            logging:
              level: "INFO"
            """).strip()
        )
        temp_file.flush()

        # Use StringIO to capture output
        output = io.StringIO()

        # Print the config
        _, issues = print_config(temp_file.name, output=output)

        # Verify there are no issues
        assert issues == []

        # Verify the output contains expected strings
        output_text = output.getvalue()
        assert "Configuration is valid" in output_text
        assert "Provider Defaults" in output_text
        assert "default_model: ollama:llama3.1:8b" in output_text
        assert "level: INFO" in output_text


def test_print_config_invalid_file() -> None:
    """Prints validation issues for an invalid configuration file."""
    # Create a temporary YAML file with issues
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            provider_defaults:
              some_other_setting: "value"
            logging:
              level: "TRACE"  # Invalid log level
            """).strip()
        )
        temp_file.flush()

        # Use StringIO to capture output
        output = io.StringIO()

        # Print the config
        _, issues = print_config(temp_file.name, output=output)

        # Verify there are issues
        assert len(issues) > 0

        # Verify specific issues
        assert any("Missing default_model" in issue for issue in issues)
        assert any("Invalid log level" in issue for issue in issues)

        # Verify the output contains the issues
        output_text = output.getvalue()
        assert "Configuration validation issues" in output_text
        assert "Missing default_model" in output_text
        assert "Invalid log level" in output_text


def test_print_config_nonexistent_file() -> None:
    """Returns error when file does not exist."""
    # Use a nonexistent file path
    output = io.StringIO()
    _, issues = print_config("/nonexistent/path/to/config.yaml", output=output)

    # Verify there's a config loading error
    assert len(issues) == 1
    assert "Error loading configuration" in issues[0]
    assert "Config file not found" in issues[0]

    # Verify the output contains the expected message
    output_text = output.getvalue()
    assert "Error loading configuration" in output_text


def test_print_config_no_validation() -> None:
    """Prints configuration without validation."""
    # Create a temporary YAML file with issues
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(
            dedent("""
            provider_defaults:
              some_other_setting: "value"
            logging:
              level: "TRACE"  # Would be invalid if validated
            """).strip()
        )
        temp_file.flush()

        # Use StringIO to capture output
        output = io.StringIO()

        # Print the config without validation
        _, issues = print_config(temp_file.name, output=output, validate=False)

        # Verify there are no issues reported
        assert issues == []

        # Verify the output doesn't contain validation messages
        output_text = output.getvalue()
        assert "Configuration is valid" not in output_text
        assert "Configuration validation issues" not in output_text