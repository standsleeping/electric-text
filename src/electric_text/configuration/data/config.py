from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for the electric_text system.

    This dataclass encapsulates all configuration parameters for the
    electric_text system loaded from YAML configuration files.

    Attributes:
        provider_defaults: Default settings for providers (primarily default_model)
        tool_boxes: Available tool boxes configuration
        logging: Logging configuration (primarily level)
        http_logging: HTTP logging configuration (enabled and log_dir)
        shorthands: Shorthand configuration for providers and models
        raw_config: The raw configuration dictionary
    """

    provider_defaults: Dict[str, Any]
    tool_boxes: Dict[str, List[str]]
    logging: Dict[str, Any]
    http_logging: Dict[str, Any]
    shorthands: Dict[str, Any]
    raw_config: Dict[str, Any]

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create a Config instance from a dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Config instance
        """
        return cls(
            provider_defaults=config_dict.get("provider_defaults", {}),
            tool_boxes=config_dict.get("tool_boxes", {}),
            logging=config_dict.get("logging", {"level": "ERROR"}),
            http_logging=config_dict.get("http_logging", {"enabled": False, "log_dir": "./http_logs"}),
            shorthands=config_dict.get("shorthands", {"provider_names": {}, "models": {}}),
            raw_config=config_dict,
        )
