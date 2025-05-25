from pydantic import BaseModel

class DefaultOutputSchema(BaseModel):
    """Default response model for prompts without a specific model class."""
    pass