import os
import logging
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from .routes import routes


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
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

    server.mount(
        "/static",
        StaticFiles(directory="web/static"),
        name="static",
    )

    return server
