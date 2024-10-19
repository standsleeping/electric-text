from pydantic import BaseModel
from typing import Optional, List


class TemplateFragment(BaseModel):
    text: str


class UserMessage(BaseModel):
    system_message: Optional[List[TemplateFragment]] = None
    prefix_fragments: Optional[List[TemplateFragment]] = None
    prompt: str
    suffix_fragments: Optional[List[TemplateFragment]] = None


class OutputSchema(BaseModel):
    schema_json: str


class ResponseItem(BaseModel):
    item_json: str


class Response(BaseModel):
    prompt: UserMessage
    schema: OutputSchema
    response_items: List[ResponseItem]
