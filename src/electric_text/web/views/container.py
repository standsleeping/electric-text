def container(
    *,
    content: str = "",
    padding: str = "var(--spacing-4)",
    preset: str | None = None,
    styles: dict[str, str] | None = None,
) -> str:
    presets = {
        "centered": {
            "padding": padding,
            "display": "flex",
            "flex-direction": "column",
            "align-items": "center",
            "justify-content": "center",
            "gap": "var(--spacing-4)",
            "max-width": "64rem",
            "margin": "0 auto",
            "width": "100%",
        },
        "standard": {
            "padding": padding,
            "display": "flex",
            "flex-direction": "column",
            "gap": "var(--spacing-4)",
        },
    }

    if preset and preset in presets:
        combined_styles = {**presets[preset], **(styles or {})}
    else:
        combined_styles = styles or {}

    if combined_styles:
        style_str = "; ".join(f"{k}: {v}" for k, v in combined_styles.items())
        return f"<div style='{style_str}'>{content}</div>"
    else:
        return f"<div>{content}</div>"
