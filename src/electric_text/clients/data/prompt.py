from typing import Optional, List
from dataclasses import dataclass, field

from electric_text.clients.data.template_fragment import TemplateFragment


@dataclass
class Prompt:
    prompt: str
    system_message: Optional[List[TemplateFragment]] = field(default=None)
    prefix_fragments: Optional[List[TemplateFragment]] = field(default=None)
    suffix_fragments: Optional[List[TemplateFragment]] = field(default=None)

