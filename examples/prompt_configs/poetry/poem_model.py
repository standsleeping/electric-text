from pydantic import BaseModel, Field
from typing import List, Optional


class PoemResponse(BaseModel):
    """Model representing the response from the poetry generation prompt."""
    
    title: str = Field(
        description="The title of the generated poem"
    )
    
    poem: str = Field(
        description="The full text of the generated poem"
    )
    
    style_notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the style or form of the poem"
    )
    
    themes: List[str] = Field(
        default_factory=list,
        description="Key themes or topics in the poem"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Autumn Leaves",
                    "poem": "Golden leaves fall,\nDancing in the autumn breeze.\nTime passes slowly.",
                    "style_notes": "Haiku form with traditional nature imagery",
                    "themes": ["autumn", "nature", "impermanence"]
                }
            ]
        }
    }