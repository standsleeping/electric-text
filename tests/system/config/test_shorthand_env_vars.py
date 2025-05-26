import pytest
from httpx import Response

from electric_text.cli.functions.main import main


@pytest.mark.asyncio
async def test_cli_with_env_var_shorthand(fake_http, capsys, monkeypatch):
    """Test CLI with environment variable shorthand configuration."""

    custom_shorthand = "custom-shorthand"

    env_val = f"claude-3-7-sonnet-20250219++{custom_shorthand}"

    monkeypatch.setenv("ANTHROPIC_MODEL_SHORTHAND_ABC", env_val)

    fake_http.post("https://api.anthropic.com/v1/messages").mock(
        return_value=Response(
            200,
            json={
                "id": "id-456",
                "type": "message",
                "role": "assistant",
                "model": "claude-3-7-sonnet-20250219",
                "content": [
                    {
                        "type": "text",
                        "text": "LINE1\nLINE2\nLINE3",
                    }
                ],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 55, "output_tokens": 18},
            },
        )
    )

    exit_code = await main(
        [
            "Write a haiku.",
            "-m",
            custom_shorthand,
            "--api-key",
            "test-key",
        ]
    )

    assert exit_code == 0

    captured = capsys.readouterr()
    assert "LINE1" in captured.out
    assert "LINE2" in captured.out
    assert "LINE3" in captured.out
