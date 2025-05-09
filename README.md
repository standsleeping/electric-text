# Electric Text

Get any response from any AI model.

## Usage

Basic usage:
```bash
python -m electric_text "Write a haiku about the way rain smells when the weather starts to warm up in the American Midwest." --model ollama:llama3.1:8b
```

### Options

- `text_input`: Your text input (required positional argument)
- `--model`, `-m`: Model to use for processing (default: ollama:llama3.1:8b)
- `--log-level`, `-l`: Set the logging level to DEBUG, INFO, WARNING, ERROR, or CRITICAL (default: ERROR)
- `--api-key`, `-k`: API key for providers that require authentication (e.g., Anthropic)
- `--max-tokens`, `-mt`: Maximum number of tokens to generate
- `--prompt-name`, `-p`: Name of the prompt to use (see below)
- `--stream`, `-st`: Stream the response (flag)

Example with options:
```bash
python -m electric_text "Write a haiku about the way rain smells when the weather starts to warm up in the American Midwest." \
  --model ollama:llama3.1:8b \
  --log-level DEBUG \
  --api-key your_api_key \
  --max-tokens 1000
```

### Reusable Prompts

Configure reusable prompts with structured responses by creating a JSON file in the `USER_PROMPT_DIRECTORY` directory.

**Note:** Before using these prompt examples, you need to set the `USER_PROMPT_DIRECTORY` environment variable to point to the directory containing your prompt configurations.

There are some example prompts (structured and unstructured) in the `examples/prompt_configs` directory.

```bash
export USER_PROMPT_DIRECTORY="/path/to/electric-text/examples/prompt_configs"
```

#### Structured Schema Generation
Convert natural language to structured data:
```bash
python -m electric_text "The car weighs 5,000 pounds, costs $25,000, and has a range of 400 miles." \
  --prompt-name prose_to_schema
```

#### Streaming Structured Schema
Same as above but with streaming output:
```bash
python -m electric_text "The car weighs 5,000 pounds, costs $25,000, and has a range of 400 miles." \
  --prompt-name prose_to_schema \
  --stream
```

#### Poetry Generation
Generate poetry based on a topic:
```bash
python -m electric_text "Write a haiku about the way rain smells when the weather starts to warm up in the American Midwest." \
  --prompt-name poetry
```

#### Streaming Poetry
Generate poetry with streaming output:
```bash
python -m electric_text "Write a haiku about the way rain smells when the weather starts to warm up in the American Midwest." \
  --prompt-name poetry \
  --stream
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

#### Examples:

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