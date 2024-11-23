import unittest

from core.entities import (
    ResponseItem,
    TemplateFragment,
    Prompt,
    OutputSchema,
    Response,
)


class TestResponse(unittest.TestCase):
    def test_model_response_structure(self):
        system_fragments = [TemplateFragment(text="system-message")]
        prefix_fragments = [TemplateFragment(text="prefix-fragment")]
        suffix_fragments = [TemplateFragment(text="suffix-fragment")]

        user_message = Prompt(
            system_message=system_fragments,
            prefix_fragments=prefix_fragments,
            prompt="user-prompt",
            suffix_fragments=suffix_fragments,
        )

        output_schema = OutputSchema(output_json='{"key": "value"}')

        response_items = [
            ResponseItem(item_json='{"item": "response1"}'),
            ResponseItem(item_json='{"item": "response2"}'),
        ]

        model_response = Response(
            prompt=user_message, output_schema=output_schema, response_items=response_items
        )

        assert model_response.prompt == user_message
        assert model_response.output_schema == output_schema
        assert len(model_response.response_items) == 2
        assert model_response.response_items[0].item_json == '{"item": "response1"}'
        assert model_response.response_items[1].item_json == '{"item": "response2"}'
        assert model_response.prompt.prompt == "user-prompt"
        assert model_response.prompt.system_message == system_fragments
        assert model_response.prompt.prefix_fragments == prefix_fragments
        assert model_response.prompt.suffix_fragments == suffix_fragments
