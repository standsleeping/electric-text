import os
import json
import glob
from pathlib import Path
from typing import List
from electric_text.prompting.data.prompt_config import PromptConfig
from electric_text.prompting.functions.get_prompt_directory import get_prompt_directory


def get_prompt_list() -> List[PromptConfig]:
    """
    Get a list of all prompt configurations from the configured prompt directory.

    Loads configurations from JSON files, where each config specifies:
    - name: Name of the prompt
    - description: Description of what the prompt does
    - system_message_path: Path to the text file containing the system message
    - model_path: Optional path to Python file containing a validation model for response validation

    Returns:
        List[PromptConfig]: A list of prompt configurations.
    """
    prompt_dir = get_prompt_directory()

    prompt_configs = []
    json_files = glob.glob(os.path.join(prompt_dir, "*.json"))

    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                config_data = json.load(f)

            # Convert relative paths to absolute if needed
            base_dir = Path(prompt_dir)
            system_path = config_data.get("system_message_path", "")

            # Handle model_path (previously schema_path)
            model_path = config_data.get("model_path", None)

            # For backward compatibility, check schema_path if model_path is not provided
            if model_path is None and "schema_path" in config_data:
                print(f"Use 'model_path' instead of 'schema_path' in {json_file}.")
                model_path = config_data.pop("schema_path")
                config_data["model_path"] = model_path

            if system_path and not os.path.isabs(system_path):
                config_data["system_message_path"] = str(base_dir / system_path)

            if model_path and not os.path.isabs(model_path):
                config_data["model_path"] = str(base_dir / model_path)

            # Add the name based on filename if not present
            if "name" not in config_data:
                config_data["name"] = Path(json_file).stem

            prompt_config = PromptConfig(**config_data)
            prompt_configs.append(prompt_config)

        except Exception as e:
            # Log the error but continue processing other files
            print(f"Error loading prompt config from {json_file}: {e}")

    return prompt_configs
