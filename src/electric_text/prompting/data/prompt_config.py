import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, cast


@dataclass
class PromptConfig:
    """Model representing a prompt configuration loaded from JSON files."""

    name: str
    """Name of the prompt"""

    description: str
    """Description of what the prompt does"""

    system_message_path: str
    """Path to the text file containing the system message"""

    schema_path: Optional[str] = None
    """Optional path to JSON schema file for response validation"""

    def get_system_message(self) -> str:
        """Load the system message from the specified path."""
        with open(self.system_message_path, "r") as f:
            return f.read()

    def get_schema(self) -> Optional[Dict[str, Any]]:
        """Load the JSON schema from the specified path if it exists."""
        if not self.schema_path:
            return None

        with open(self.schema_path, "r") as f:
            return cast(Dict[str, Any], json.load(f))
