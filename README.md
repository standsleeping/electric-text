# Electric Text

Get any response from any AI model.

## Usage

Basic usage:
```bash
python -m electric_text "Write a haiku about how rain smells in the early summer."
```

### Options

- `text_input`: Your text input (required positional argument)
- `--model`, `-m`: Model to use for processing (default: ollama:llama3.1:8b)
- `--log-level`, `-l`: Set the logging level to DEBUG, INFO, WARNING, ERROR, or CRITICAL (default: ERROR)
- `--api-key`, `-k`: API key for providers that require authentication (e.g., Anthropic)
- `--max-tokens`, `-mt`: Maximum number of tokens to generate
- `--prompt-name`, `-p`: Name of the prompt to use (see below)
- `--stream`, `-st`: Stream the response (flag)
- `--tool-boxes`, `-tb`: List of tool boxes to use (comma-separated, e.g., "meteorology,travel")
- `--config`, `-c`: Path to configuration file

Example with options:
```bash
python -m electric_text "Write a haiku about how rain smells in the early summer." \
  --model ollama:llama3.1:8b \
  --log-level DEBUG \
  --api-key your_api_key \
  --max-tokens 1000 \
  --tool-boxes meteorology
```

## Configuration

Electric Text supports YAML configuration files for centralizing your settings. This allows you to configure the default model and logging settings.

### Setting Up Your Config

Copy the example configuration file to one of the standard locations:

```bash
# Copy to your home directory (recommended)
mkdir -p ~/.electric_text
cp examples/config.yaml ~/.electric_text/
```

You can also set the environment variable to point to your configuration:

```bash
export ELECTRIC_TEXT_CONFIG="/path/to/your/config.yaml"
```

### Configuration File Locations

The system looks for configuration files in the following order:

1. Path specified via the `--config` command-line argument
2. Path specified in the `ELECTRIC_TEXT_CONFIG` environment variable
3. Default locations:
   - `./config.yaml` (current directory)
   - `~/.electric_text/config.yaml` (user's home directory)
   - `/etc/electric_text/config.yaml` (system-wide)

### Checking Your Configuration

To view and validate your current configuration, use the config command:

```bash
python -m electric_text config
```

You can also specify a different configuration file:

```bash
python -m electric_text config --config path/to/config.yaml
```

## Environment Variables

Electric Text uses environment variables with the `ELECTRIC_TEXT_` prefix for configuration.

### Configuration Variables

```bash
# Configuration file path
export ELECTRIC_TEXT_CONFIG=/path/to/your/config.yaml

# Logging level
export ELECTRIC_TEXT_LOG_LEVEL=INFO
```

### API Keys

```bash
# Provider API keys
export ELECTRIC_TEXT_ANTHROPIC_API_KEY=your_anthropic_key
export ELECTRIC_TEXT_OPENAI_API_KEY=your_openai_key
export ELECTRIC_TEXT_OLLAMA_API_KEY=your_ollama_key
```

### Directory Paths

```bash
# Directory containing your custom prompt configurations
export ELECTRIC_TEXT_PROMPT_DIRECTORY=/path/to/your/prompt_configs

# Directory containing your custom tool configurations  
export ELECTRIC_TEXT_TOOLS_DIRECTORY=/path/to/your/tool_configs
```

### HTTP Logging

```bash
# Enable HTTP request/response logging for debugging
export ELECTRIC_TEXT_HTTP_LOGGING=true

# Directory for HTTP log files (defaults to ./http_logs)
export ELECTRIC_TEXT_HTTP_LOG_DIR=/path/to/http/logs
```

### Model Shorthands

```bash
# Provider name shorthands
# Pattern: ELECTRIC_TEXT_{PROVIDER}_PROVIDER_NAME_SHORTHAND=canonical_name++shorthand
export ELECTRIC_TEXT_OLLAMA_PROVIDER_NAME_SHORTHAND=ollama++lma

# Model shorthands  
# Pattern: ELECTRIC_TEXT_{PROVIDER}_MODEL_SHORTHAND_{NAME}=canonical_model++shorthand
export ELECTRIC_TEXT_OLLAMA_MODEL_SHORTHAND_SMALL=llama3.1:8b++31
export ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_SONNET=claude-3-7-sonnet-20250219++claude3
export ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_GPT4=gpt-4o++gpt4
```


## Reusable Prompts

Configure reusable prompts with structured responses by creating a JSON file in the `ELECTRIC_TEXT_PROMPT_DIRECTORY` directory.

**Note:** Before using these prompt examples, you need to set the `ELECTRIC_TEXT_PROMPT_DIRECTORY` environment variable to point to the directory containing your prompt configurations.

```bash
export ELECTRIC_TEXT_PROMPT_DIRECTORY="/path/to/electric-text/examples/prompt_configs"
```

### Examples

These examples are provided to help you get started. You can find more examples in the `examples/prompt_configs` directory.

Convert natural language to structured data:
```bash
python -m electric_text "The car weighs 5,000 pounds, costs $25,000, and has a range of 400 miles." \
  --prompt-name prose_to_schema
```

Same as above but with streaming output:
```bash
python -m electric_text "The car weighs 5,000 pounds, costs $25,000, and has a range of 400 miles." \
  --prompt-name prose_to_schema \
  --stream
```

Generate poetry based on a topic:
```bash
python -m electric_text "Write a haiku about how rain smells when early summer arrives in the American Midwest." \
  --prompt-name poetry
```

## Tool Boxes

Electric Text supports tool boxes, which are collections of tools that can be used by models to perform specific tasks.

### Configuring Tool Boxes

Tool boxes are defined in JSON files in the tool configs directory. Each tool box is a collection of tools that can be used together.

**Note:** Before using tool boxes, set the `ELECTRIC_TEXT_TOOLS_DIRECTORY` environment variable to point to your tool configs directory. If not set, the system will use the default `examples/tool_configs` directory.

```bash
export ELECTRIC_TEXT_TOOLS_DIRECTORY="/path/to/electric-text/examples/tool_configs"
```

The directory should contain:
1. A `tool_boxes.json` file that defines collections of tools
2. Individual JSON files for each tool

Example tool box configuration:
```json
[
    {
        "name": "meteorology",
        "description": "Tools for meteorology",
        "tools": [
            "get_current_weather",
            "get_forecast"
        ]
    }
]
```

Each tool is defined in its own JSON file with details about its parameters and functionality:

```json
{
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. Omaha, NE"
            },
            "unit": {
                "type": "string",
                "enum": [
                    "celsius",
                    "fahrenheit"
                ]
            }
        },
        "required": [
            "location"
        ]
    }
}
```

### Using Tool Boxes

To use tool boxes in your requests, use the `--tool-boxes` or `-tb` option:

```bash
python -m electric_text "What's the weather like in Omaha?" \
  --model gpt4 \
  --tool-boxes meteorology
```

You can specify multiple tool boxes:

```bash
python -m electric_text "Plan a trip to Chicago and check the weather." \
  --model claude3 \
  --tool-boxes meteorology,travel
```

## Model Shorthands

Electric Text supports custom model shorthands to make it easier to reference your frequently used models.

### Using Shorthands

Instead of typing the full provider and model names, you can use shorthand references:

```bash
# Using a shorthand
python -m electric_text "What is the capital of Nebraska?" --model gpt4
```

### Defining Custom Shorthands

You can define custom shorthands in the YAML config:

```
(Coming Soon)
```

You can also define custom shorthands by setting environment variables:

1. **Provider Shorthands**: Maps a shorthand to a provider name
   ```
   export ELECTRIC_TEXT_{PROVIDER}_PROVIDER_NAME_SHORTHAND="canonical_provider++shorthand"
   ```

2. **Model Shorthands**: Maps a shorthand to a specific provider and model
   ```
   export ELECTRIC_TEXT_{PROVIDER}_MODEL_SHORTHAND_{NAME}="canonical_model++shorthand"
   ```

#### Examples

```bash
# Define "antro" as a shorthand for "anthropic" provider
export ELECTRIC_TEXT_ANTHROPIC_PROVIDER_NAME_SHORTHAND="anthropic++antro"

# Define "claude3" as a shorthand for Claude 3 Sonnet
export ELECTRIC_TEXT_ANTHROPIC_MODEL_SHORTHAND_SONNET="claude-3-7-sonnet-20250219++claude3"

# Define "gpt4" as a shorthand for GPT-4o
export ELECTRIC_TEXT_OPENAI_MODEL_SHORTHAND_GPT4="gpt-4o++gpt4"
```

After setting these environment variables, you can use the shorthands in your commands:

```bash
python -m electric_text "Hello world" --model claude3
```

## Subcommands

Electric Text supports subcommands. Right now, we just support a `config` subcommand.

#### config

View and validate your configuration:

```bash
python -m electric_text config
```

Options:
- `--config`, `-c`: Path to configuration file
- `--no-validate`, `-n`: Skip validation (only print configuration)

Example:
```bash
# Check configuration using a specific file
python -m electric_text config --config path/to/config.yaml

# Print configuration without validation
python -m electric_text config --no-validate
```

For more details, see the [Configuration System Documentation](src/electric_text/configuration/README.md).

## HTTP Logging

Electric Text includes built-in HTTP logging functionality that captures all API requests and responses for debugging.

### Quick Start

Enable HTTP logging by setting environment variables:

```bash
# Enable logging
export ELECTRIC_TEXT_HTTP_LOGGING=true

# Optionally set custom log directory (defaults to ./http_logs)
export ELECTRIC_TEXT_HTTP_LOG_DIR=/path/to/logs

# Run your code
python -m electric_text "Write a haiku about rain" --model gpt-4o
```

### Using with VS Code Debugger

Add these environment variables to your `.vscode/launch.json` configuration:

```json
{
  "name": "My Config",
  "type": "debugpy",
  "request": "launch",
  "module": "electric_text",
  "args": ["Your prompt here", "-m", "ollama:llama3.1:8b"],
  "env": {
    "ELECTRIC_TEXT_HTTP_LOGGING": "true",
    "ELECTRIC_TEXT_HTTP_LOG_DIR": "${workspaceFolder}/http_logs"
  }
}
```

### Log Format

Each HTTP interaction is saved as a JSON file with the following structure:

```json
{
  "timestamp": "2024-01-01T10:10:10.123456",
  "method": "POST",
  "url": "https://api.openai.com/v1/chat/completions",
  "request": {
    "headers": { ... },
    "body": { ... }
  },
  "response": {
    "status": 200,
    "headers": { ... },
    "body": { ... }
  },
  "duration_ms": 123.45,
  "provider": "openai",
  "model": "gpt-4o",
  "error": null
}
```

## Python Interface

You can import and use the `generate` function directly:

```python

from electric_text import generate

result = await generate(
    text_input="Some prompt input",
    provider_name="ollama",
    model_name="llama3.1:8b"
)

# Access the result
print(result.text.content)

# Or check the response type
if result.response_type.value == "TEXT":
    print("Got text response:", result.text.content)
elif result.response_type.value == "DATA":
    print("Got structured data:", result.data.data)
elif result.response_type.value == "TOOL_CALL":
    print("Got tool call:", result.tool_call.name)
```

### Parameters

All the same parameters from the CLI are available as function arguments:

```python
result = await generate(
    text_input="Analyze this data: temperature=72, humidity=45%",
    provider_name="anthropic",
    model_name="claude-3-7-sonnet-20250219",
    api_key="your-api-key-here",  # Optional, can use env vars
    max_tokens=1000,
    prompt_name="prose_to_schema",  # Use custom prompts
    tool_boxes="meteorology,analysis",  # Use tool boxes
    log_level="DEBUG"
)
```

## Note for AI Coding Assistants

Are you an AI coding assistant?

Please refer to the [CLAUDE.md](CLAUDE.md) file for information about the project.