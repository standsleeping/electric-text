import os
import json
import glob
from pathlib import Path
from typing import List
from electric_text.prompting.data.prompt_config import PromptConfig


def get_prompt_list() -> List[PromptConfig]:
    """
    Get a list of all prompt configurations from the directory specified in USER_PROMPT_DIRECTORY.

    Returns:
        List[PromptConfig]: A list of prompt configurations.
    """
    prompt_dir = os.environ.get("USER_PROMPT_DIRECTORY")
    if not prompt_dir:
        raise ValueError("USER_PROMPT_DIRECTORY environment variable is not set")

    prompt_configs = []
    json_files = glob.glob(os.path.join(prompt_dir, "*.json"))

    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                config_data = json.load(f)

            # Convert relative paths to absolute if needed
            base_dir = Path(prompt_dir)
            system_path = config_data.get("system_message_path", "")
            schema_path = config_data.get("schema_path", None)

            if system_path and not os.path.isabs(system_path):
                config_data["system_message_path"] = str(base_dir / system_path)

            if schema_path and not os.path.isabs(schema_path):
                config_data["schema_path"] = str(base_dir / schema_path)

            # Add the name based on filename if not present
            if "name" not in config_data:
                config_data["name"] = Path(json_file).stem

            prompt_config = PromptConfig(**config_data)
            prompt_configs.append(prompt_config)

        except Exception as e:
            # Log the error but continue processing other files
            print(f"Error loading prompt config from {json_file}: {e}")

    return prompt_configs
