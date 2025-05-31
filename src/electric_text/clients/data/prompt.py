from typing import List
from dataclasses import dataclass, field

from electric_text.clients.data.template_fragment import TemplateFragment


@dataclass
class Prompt:
    prompt: str
    system_message: List[TemplateFragment] = field(default_factory=list)
    prefix_fragments: List[TemplateFragment] = field(default_factory=list)
    suffix_fragments: List[TemplateFragment] = field(default_factory=list)

