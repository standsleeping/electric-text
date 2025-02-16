from .render_html import render_html


def prompt_form(post_url: str) -> str:
    return render_html(
        "prompt-form.html",
        {
            "post_url": post_url,
            "form_id": "prompt-form",
            "debounce_ms": "300",
        },
    )
