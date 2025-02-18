from .render_html import render_html
from ..domain import ROOT_PAGE


def nav() -> str:
    home_path = ROOT_PAGE

    template_data = {
        "home_path": home_path,
    }

    template_name = "nav.html"

    return render_html(template_name, template_data)
