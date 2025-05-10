# Electric Text

Get any response from any AI model.

## Usage

Basic usage:
```bash
python -m electric_text "Write a haiku about how rain smells when early summer arrives in the American Midwest." --model ollama:llama3.1:8b
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

Example with options:
```bash
python -m electric_text "Write a haiku about how rain smells when early summer arrives in the American Midwest." \
  --model ollama:llama3.1:8b \
  --log-level DEBUG \
  --api-key your_api_key \
  --max-tokens 1000 \
  --tool-boxes meteorology
```

## Setting up your environment

The following environment variables control the behavior of Electric Text. More details on these variables are provided below.

```bash
# Specify a provider API key.
# General pattern: [PROVIDER]_API_KEY=your_api_key
export ANTHROPIC_API_KEY=your_api_key

# Specify shorthands for a provider name.
# General pattern: [PROVIDER]_PROVIDER_NAME_SHORTHAND=canonical_name++shorthand
export OLLAMA_PROVIDER_NAME_SHORTHAND=lma

# Specify shorthands for a model name.
# General pattern: [PROVIDER]_MODEL_SHORTHAND_*=canonical_model++shorthand
export OLLAMA_MODEL_SHORTHAND_SMALL=llama3.1:8b++31

# Specify the path to your prompt configs.
export USER_PROMPT_DIRECTORY=path/to/your/prompt_configs

# Specify the path to your tool configurations.
export USER_TOOL_CONFIGS_DIRECTORY=path/to/your/tool_configs
```

## Canonical names

The following are the canonical names for the providers and models that Electric Text supports.

```bash
(Coming soon...)
```

## Reusable Prompts

Configure reusable prompts with structured responses by creating a JSON file in the `USER_PROMPT_DIRECTORY` directory.

**Note:** Before using these prompt examples, you need to set the `USER_PROMPT_DIRECTORY` environment variable to point to the directory containing your prompt configurations.

```bash
export USER_PROMPT_DIRECTORY="/path/to/electric-text/examples/prompt_configs"
```

### Example reusable prompts

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

**Note:** Before using tool boxes, set the `USER_TOOL_CONFIGS_DIRECTORY` environment variable to point to your tool configs directory. If not set, the system will use the default `examples/tool_configs` directory.

```bash
export USER_TOOL_CONFIGS_DIRECTORY="/path/to/electric-text/examples/tool_configs"
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

You can define custom shorthands by setting environment variables:

1. **Provider Shorthands**: Maps a shorthand to a provider name
   ```
   export PROVIDER_PROVIDER_NAME_SHORTHAND="canonical_provider++shorthand"
   ```

2. **Model Shorthands**: Maps a shorthand to a specific provider and model
   ```
   export PROVIDER_MODEL_SHORTHAND_NAME="canonical_model++shorthand"
   ```

#### Model shorthand examples:

```bash
# Define "antro" as a shorthand for "anthropic" provider
export ANTHROPIC_PROVIDER_NAME_SHORTHAND="anthropic++antro"

# Define "claude3" as a shorthand for Claude 3 Sonnet
export ANTHROPIC_MODEL_SHORTHAND_SONNET="claude-3-7-sonnet-20250219++claude3"

# Define "gpt4" as a shorthand for GPT-4o
export OPENAI_MODEL_SHORTHAND_GPT4="gpt-4o++gpt4"
```

After setting these environment variables, you can use the shorthands in your commands:

```bash
python -m electric_text "Hello world" --model claude3
```

## Note for AI Coding Assistants

Are you an AI coding assistant?

Please refer to the [CLAUDE.md](CLAUDE.md) file for information about the project.