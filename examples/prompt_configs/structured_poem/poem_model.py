from pydantic import BaseModel, Field
from typing import List, Optional


class Poem(BaseModel):
    """Model representing the structure of a poem."""

    title: str = Field(description="The title of the poem")

    author: Optional[str] = Field(
        default=None, description="The name of the poet who wrote the poem"
    )

    stanzas: List[List[str]] = Field(
        description="A list of stanzas, where each stanza is a list of lines"
    )

    form: Optional[str] = Field(
        default=None, description="The poetic form (e.g., sonnet, haiku, free verse)"
    )

    rhyme_scheme: Optional[str] = Field(
        default=None, description="The pattern of rhymes (e.g., ABAB, AABB)"
    )

    meter: Optional[str] = Field(
        default=None, description="The metrical pattern (e.g., iambic pentameter)"
    )

    themes: Optional[List[str]] = Field(
        default=None, description="List of themes present in the poem"
    )

    year_published: Optional[int] = Field(
        default=None, description="The year the poem was published"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Road Not Taken",
                    "author": "Robert Frost",
                    "stanzas": [
                        [
                            "Two roads diverged in a yellow wood,",
                            "And sorry I could not travel both",
                            "And be one traveler, long I stood",
                            "And looked down one as far as I could",
                            "To where it bent in the undergrowth;",
                        ],
                        [
                            "Then took the other, as just as fair,",
                            "And having perhaps the better claim,",
                            "Because it was grassy and wanted wear;",
                            "Though as for that the passing there",
                            "Had worn them really about the same,",
                        ],
                    ],
                    "form": "Narrative poem",
                    "rhyme_scheme": "ABAAB",
                    "themes": ["Choice", "Life journey", "Regret"],
                    "year_published": 1916,
                }
            ]
        }
    }
