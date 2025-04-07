from pydantic import BaseModel
from typing import Optional, List

from electric_text.clients.data.template_fragment import TemplateFragment


class Prompt(BaseModel):
    system_message: Optional[List[TemplateFragment]] = None
    prefix_fragments: Optional[List[TemplateFragment]] = None
    prompt: str
    suffix_fragments: Optional[List[TemplateFragment]] = None
