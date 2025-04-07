from electric_text.clients.data.prompt import Prompt


def convert_to_llm_messages(prompt: Prompt) -> list[dict[str, str]]:
    if prompt.system_message is None:
        raise ValueError("System message is required")

    system_message = [
        {"role": "system", "content": fragment.text}
        for fragment in prompt.system_message
    ]

    return system_message + [{"role": "user", "content": prompt.prompt}]
