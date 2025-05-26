import pytest
from httpx import Response

from electric_text.cli.functions.main import main


@pytest.mark.asyncio
async def test_simple_prompt(fake_http, capsys):
    """Test main() function with command-line arguments."""

    fake_http.post("https://api.anthropic.com/v1/messages").mock(
        return_value=Response(
            200,
            json={
                "id": "id-123",
                "type": "message",
                "role": "assistant",
                "model": "claude-3-7-sonnet-20250219",
                "content": [
                    {
                        "type": "text",
                        "text": "Gentle drops descend\nOn golden fields of corn silk\nSummer's gift to earth",
                    }
                ],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 50, "output_tokens": 20},
            },
        )
    )

    exit_code = await main(
        [
            "Write a haiku about rain in farm fields",
            "--model",
            "anthropic:claude-3-7-sonnet-20250219",
            "--api-key",
            "test-key",
        ]
    )

    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Gentle drops descend" in captured.out
    assert "On golden fields" in captured.out
    assert "Summer's gift to earth" in captured.out
