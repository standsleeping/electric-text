from pydantic import BaseModel


class TemplateFragment(BaseModel):
    text: str
