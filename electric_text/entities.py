from pydantic import BaseModel
from typing import Optional, List


class TemplateFragment(BaseModel):
    text: str


class Prompt(BaseModel):
    system_message: Optional[List[TemplateFragment]] = None
    prefix_fragments: Optional[List[TemplateFragment]] = None
    prompt: str
    suffix_fragments: Optional[List[TemplateFragment]] = None


class OutputSchema(BaseModel):
    output_json: str


class ResponseItem(BaseModel):
    item_json: str


class Response(BaseModel):
    prompt: Prompt
    output_schema: OutputSchema
    response_items: List[ResponseItem]
