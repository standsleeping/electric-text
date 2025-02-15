import uuid
import asyncio
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.requests import Request
from starlette.routing import Route
from typing import AsyncGenerator
from .views.nav import nav
from .views.render_html import render_html
from .views.container import container
from .views.prompt_form import prompt_form
from .domain import SUBMIT_PROMPT, ROOT_PAGE, RESPONSE_STREAM

def render_page(*, title: str, content: str) -> HTMLResponse:
    nav_html = nav()
    return HTMLResponse(
        render_html(
            "page.html",
            {
                "title": title,
                "content": content,
                "nav": nav_html,
            },
        )
    )


async def root_page(request: Request) -> HTMLResponse:
    prompt_form_html = prompt_form(post_url=SUBMIT_PROMPT)
    return render_page(
        title="ElectricText",
        content=container(
            preset="standard",
            padding="0",
            content=prompt_form_html,
        ),
    )


async def submit_prompt(request: Request) -> HTMLResponse:
    form = await request.form()
    prompt = form.get("prompt")
    prompt_id = str(uuid.uuid4())

    response_area = f"""
    <div id="response-area" hx-ext="sse" sse-connect="{RESPONSE_STREAM}?prompt_id={prompt_id}" sse-swap="SomeEventName" sse-close="StreamClosing">
        (Generating response for prompt: {prompt})
    </div>
    """

    return HTMLResponse(response_area)


async def response_stream(request: Request) -> StreamingResponse:
    prompt_id = request.query_params.get("prompt_id", "unknown")
    max_events = int(request.query_params.get("max_events", 10))

    return StreamingResponse(
        event_stream(prompt_id, max_events), media_type="text/event-stream"
    )


async def event_stream(prompt_id: str, max_events: int) -> AsyncGenerator[str, None]:
    event_count = 0
    while True:
        data = f"event: SomeEventName\ndata: <div style='font-family: monospace;'>Prompt ID {prompt_id}: ({uuid.uuid4()})</div>\n\n"
        yield data
        await asyncio.sleep(0.5)
        event_count += 1
        if max_events and event_count >= max_events:
            yield "event: StreamClosing\ndata: N/A\n\n"
            break


routes = [
    Route(ROOT_PAGE, root_page),
    Route(SUBMIT_PROMPT, submit_prompt, methods=["POST"]),
    Route(RESPONSE_STREAM, response_stream, methods=["GET"]),
]
