from starlette.applications import Starlette
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from .routes import routes


def create_app() -> Starlette:
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
