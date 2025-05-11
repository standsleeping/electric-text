from typing import List, Dict, Optional


def convert_prompt_to_messages(
    system_messages: Optional[List[str]],
    prompt_text: str
) -> List[Dict[str, str]]:
    if system_messages is None:
        raise ValueError("System message is required")

    system_message = [
        {"role": "system", "content": message}
        for message in system_messages
    ]

    return system_message + [{"role": "user", "content": prompt_text}]
