from .render_html import render_html


def prompt_form(
    *,
    post_url: str,
    stream_url: str,
    connection_id: str = "",
    cancel_url: str = "",
    debounce_ms: int = 300,
) -> str:
    return render_html(
        "prompt-form.html",
        {
            "form_id": "prompt-form",
            "post_url": post_url,
            "stream_url": stream_url,
            "cancel_url": cancel_url,
            "connection_id": connection_id,
            "debounce_ms": str(debounce_ms),
        },
    )
