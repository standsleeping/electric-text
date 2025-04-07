from electric_text.clients.data.template_fragment import TemplateFragment
from electric_text.clients.data.prompt import Prompt


def build_simple_prompt(system_message_text: str, user_message: str) -> Prompt:
    system_message = [TemplateFragment(text=system_message_text)]
    return Prompt(
        system_message=system_message,
        prompt=user_message,
    )
