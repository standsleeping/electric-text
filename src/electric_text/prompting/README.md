# Prompt Management

This module provides functionality for managing prompts in Electric Text. It allows users to define prompts with associated system messages and JSON schemas in a centralized location.

## Usage

### Configuration

1. Set the `USER_PROMPT_DIRECTORY` environment variable to point to a directory where your prompt configuration files are stored.

2. Create JSON configuration files for each prompt. Each file should have the following structure:

```json
{
  "name": "prompt_name",
  "description": "Description of what the prompt does",
  "system_message_path": "path/to/system_message.txt",
  "schema_path": "path/to/schema.json"
}
```

Where:
- `name`: (optional) Name of the prompt. If not provided, the filename will be used.
- `description`: Description of what the prompt does.
- `system_message_path`: Path to the text file containing the system message.
- `schema_path`: (optional) Path to a JSON schema file for response validation.

### Loading Prompts

```python
from electric_text.prompting import get_prompt_list

# Get all prompt configurations
prompt_configs = get_prompt_list()

# Use a prompt
for config in prompt_configs:
    print(f"Prompt: {config.name}")

    # Get the system message content
    system_message = config.get_system_message()

    # Get the JSON schema if available
    schema = config.get_schema()
```

