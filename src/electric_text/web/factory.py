import logging
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from electric_text.web.routes import routes
from electric_text.web.functions.get_log_level import get_log_level


def setup_logging() -> None:
    logging.basicConfig(
        level=get_log_level(),
        format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


def create_app() -> Starlette:
    setup_logging()

    server = Starlette(
        routes=routes,
        middleware=[],
        exception_handlers={
            Exception: lambda request, exc: Response(
                "An error occurred.", status_code=500
            ),
        },
    )

    static_dir = (
        Path(__file__).parent.parent.parent / "electric_text" / "web" / "static"
    )

    if not static_dir.exists():
        raise FileNotFoundError(f"Static directory does not exist: {static_dir}")

    server.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )

    return server
