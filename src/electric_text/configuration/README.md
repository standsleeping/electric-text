# Configuration System

The `electric_text` configuration system provides a flexible way to configure the library's behavior using YAML files. This allows users to define the default model, logging settings, and tool boxes in a centralized configuration file.

## Configuration File Location

The system looks for configuration files in the following locations, in order of precedence:

1. Path specified via the `--config` command-line argument
2. Path specified in the `ELECTRIC_TEXT_CONFIG` environment variable
3. Default locations:
   - `./config.yaml` (current directory)
   - `~/.electric_text/config.yaml` (user's home directory)
   - `/etc/electric_text/config.yaml` (system-wide)

## Configuration File Format

The configuration file uses YAML format. Here's an example structure:

```yaml
# Default settings for providers
provider_defaults:
  default_model: "ollama:llama3.1:8b"

# Tool boxes configuration
tool_boxes:
  meteorology:
    - get_current_weather
    - get_forecast

# Logging configuration
logging:
  level: "ERROR"
```

## Using the Configuration API

### Loading Configuration

```python
from electric_text.configuration import load_config

# Load from default locations
config = load_config()

# Load from a specific path
config = load_config("/path/to/config.yaml")
```

### Accessing Configuration Values

```python
from electric_text.configuration import get_config_value

# Get a value with a default fallback
log_level = get_config_value("logging.level", default="ERROR")

# Get the default model
default_model = get_config_value("provider_defaults.default_model", default="ollama:llama3.1:8b")

# Get tool boxes
tool_boxes = get_config_value("tool_boxes", default={})
```

### Printing and Validating Configuration

You can use the `print_config` function to display the current configuration settings and validate them:

```python
from electric_text.configuration import print_config

# Print and validate the config
config, issues = print_config()  # Loads from default locations

# Print with a specific config path
config, issues = print_config("/path/to/config.yaml")

# Print without validation
config, issues = print_config(validate=False)
```

## Command-Line Interface

The configuration system provides a command-line interface for validating and inspecting your configuration:

```bash
# View your current configuration
python -m electric_text config

# With a specific config file
python -m electric_text config --config /path/to/config.yaml

# Without validation
python -m electric_text config --no-validate
```

## Environment Variable Support

The configuration system supports specifying the configuration file path via the `ELECTRIC_TEXT_CONFIG` environment variable:

```bash
export ELECTRIC_TEXT_CONFIG="/path/to/your/config.yaml"
```

This allows for flexible configuration deployment across different environments without modifying code or command-line arguments.