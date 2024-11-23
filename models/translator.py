from core.entities import (
    Prompt,
    TemplateFragment,
)


def build_simple_prompt(system_message_text: str, user_message: str):
    system_message = [TemplateFragment(text=system_message_text)]
    return Prompt(
        system_message=system_message,
        prompt=user_message,
    )


def convert_to_llm_messages(prompt: Prompt):
    if prompt.system_message is None:
        raise ValueError("System message is required")

    system_message = [
        {"role": "system", "content": fragment.text}
        for fragment in prompt.system_message
    ]

    return system_message + [{"role": "user", "content": prompt.prompt}]
