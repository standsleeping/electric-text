import unittest
from models.translator import build_simple_prompt, convert_to_llm_messages
from electric_text import Prompt, TemplateFragment


class TestTranslator(unittest.TestCase):
    def test_build_simple_prompt(self):
        system_message = "You are a helpful assistant."
        user_message = "What's the weather like today?"

        prompt = build_simple_prompt(system_message, user_message)

        self.assertIsInstance(prompt, Prompt)
        self.assertEqual(len(prompt.system_message), 1)
        self.assertIsInstance(prompt.system_message[0], TemplateFragment)
        self.assertEqual(prompt.system_message[0].text, system_message)
        self.assertEqual(prompt.prompt, user_message)

    def test_convert_to_llm_messages(self):
        system_message = [TemplateFragment(text="You are a helpful assistant.")]
        user_message = "What's the weather like today?"
        prompt = Prompt(system_message=system_message, prompt=user_message)

        messages = convert_to_llm_messages(prompt)

        expected_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the weather like today?"},
        ]

        self.assertEqual(messages, expected_messages)

    def test_convert_to_llm_messages_multiple_system_fragments(self):
        system_message = [
            TemplateFragment(text="You are a helpful assistant."),
            TemplateFragment(text="Always be polite."),
        ]
        user_message = "What's the weather like today?"
        prompt = Prompt(system_message=system_message, prompt=user_message)

        messages = convert_to_llm_messages(prompt)

        expected_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "system", "content": "Always be polite."},
            {"role": "user", "content": "What's the weather like today?"},
        ]

        self.assertEqual(messages, expected_messages)

    def test_convert_to_llm_messages_no_system_message(self):
        prompt = Prompt(system_message=None, prompt="Hello")

        with self.assertRaises(ValueError) as context:
            convert_to_llm_messages(prompt)

        self.assertEqual(str(context.exception), "System message is required")


if __name__ == "__main__":
    unittest.main()
