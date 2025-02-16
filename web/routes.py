import uuid
import asyncio
import time
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.requests import Request
from starlette.routing import Route
from typing import AsyncGenerator, Dict
from .views.nav import nav
from .views.render_html import render_html
from .views.container import container
from .views.prompt_form import prompt_form
from .domain import SUBMIT_PROMPT, ROOT_PAGE, RESPONSE_STREAM

active_prompts: Dict[str, str] = {}


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
    prompt = form.get("prompt", "")
    prompt_id = form.get("prompt_id", "")

    if not isinstance(prompt, str):
        prompt = str(prompt)

    if not isinstance(prompt_id, str):
        prompt_id = str(prompt_id)

    if not prompt_id:
        prompt_id = str(uuid.uuid4())

    active_prompts[prompt_id] = prompt

    return HTMLResponse(
        render_html(
            "stream-response.html",
            {
                "prompt_id": prompt_id,
                "stream_url": RESPONSE_STREAM,
            },
        )
    )


async def response_stream(request: Request) -> StreamingResponse:
    prompt_id = request.query_params.get("prompt_id")

    if not prompt_id:
        return StreamingResponse(
            error_stream("No prompt ID provided"),
            media_type="text/event-stream",
        )

    if prompt_id not in active_prompts:
        return StreamingResponse(
            error_stream("Invalid or expired prompt ID"),
            media_type="text/event-stream",
        )

    prompt = active_prompts.pop(prompt_id)

    return StreamingResponse(
        process_prompt_stream(prompt_id, prompt),
        media_type="text/event-stream",
    )


async def error_stream(message: str) -> AsyncGenerator[str, None]:
    yield f"data: <div class='error'>{message}</div>\n\n"
    yield "event: StreamClosing\ndata: N/A\n\n"


async def process_prompt_stream(
    prompt_id: str, prompt: str
) -> AsyncGenerator[str, None]:
    time.sleep(3)

    for i in range(1, 11):
        message = f"[{i}] — {prompt}"
        data = f"data: <span class='message'>{message}</span><br>\n\n"
        yield data
        await asyncio.sleep(0.3)  # Simulate processing time

    yield "event: StreamClosing\ndata: N/A\n\n"


routes = [
    Route(ROOT_PAGE, root_page),
    Route(SUBMIT_PROMPT, submit_prompt, methods=["POST"]),
    Route(RESPONSE_STREAM, response_stream, methods=["GET"]),
]
