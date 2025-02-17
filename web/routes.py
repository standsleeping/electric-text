import uuid
import asyncio
import logging
from typing import AsyncGenerator, Dict, TypedDict, Any
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import HTMLResponse, StreamingResponse
from .views.nav import nav
from .views.render_html import render_html
from .views.container import container
from .views.prompt_form import prompt_form
from .domain import (
    CANCEL_STREAM,
    RESPONSE_STREAM,
    ROOT_PAGE,
    SUBMIT_PROMPT,
)
from .domain import (  # Logging
    EVENT_AWAITED,
    EVENT_PROCESSED,
    EVENT_RECEIVED,
    EVENT_STREAMED,
    STREAM_CANCEL_RECEIVED,
    STREAM_CANCELED,
    STREAM_CLOSED,
    STREAM_CREATED,
    STREAM_FAILED,
    STREAM_MISSING,
    STREAM_QUEUED,
    STREAM_REMADE,
    STREAM_REQUESTED,
    STREAM_STARTED,
    TASK_CANCEL_FAILED,
    TASK_CANCELED,
    TASK_CANCELLED,
    TASK_CHUNK_STREAMED,
    TASK_CLEARED,
    TASK_COMPLETED,
    TASK_MISSING,
    USER_TEXT_RECEIVED,
)


logger = logging.getLogger(__name__)


class EventMessage(TypedDict):
    type: str
    data: Any


class StreamState:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[EventMessage] = asyncio.Queue()
        self.task: asyncio.Task[None] | None = None
        self.is_cancelled = False


active_connections: Dict[str, StreamState] = {}


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
    connection_id = str(uuid.uuid4())
    prompt_form_html = prompt_form(
        post_url=SUBMIT_PROMPT,
        stream_url=RESPONSE_STREAM,
        cancel_url=CANCEL_STREAM,
        connection_id=connection_id,
    )

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
    prompt = str(form.get("prompt", ""))
    connection_id = str(form.get("connection_id", ""))

    logger.info(f"{USER_TEXT_RECEIVED} (cid: {connection_id})")

    if connection_id not in active_connections:
        log = f"{STREAM_MISSING} (cid: {connection_id})"
        logger.error(log)
        return HTMLResponse(log, status_code=404)

    state = active_connections[connection_id]

    prev_cancelled = state.is_cancelled
    state.is_cancelled = False
    if prev_cancelled:
        logger.info(f"{STREAM_REMADE} (cid: {connection_id})")

    await state.queue.put(
        {
            "type": "prompt",
            "data": prompt,
        }
    )

    logger.info(f"{STREAM_QUEUED} (cid: {connection_id})")
    return HTMLResponse("OK")


async def cancel_stream(request: Request) -> HTMLResponse:
    connection_id = request.query_params.get("connection_id")
    logger.info(f"{STREAM_CANCEL_RECEIVED} (cid: {connection_id})")

    if connection_id not in active_connections:
        log = f"{STREAM_MISSING} (cid: {connection_id})"
        logger.error(log)
        return HTMLResponse(log, status_code=404)

    state = active_connections[connection_id]
    state.is_cancelled = True
    logger.info(f"{STREAM_CANCELED} (cid: {connection_id})")

    if state.task:
        try:
            state.task.cancel()
            logger.info(f"{TASK_CANCELLED} (cid: {connection_id})")
        except Exception:
            log = f"{TASK_CANCEL_FAILED} (cid: {connection_id})"
            logger.error(log)
            return HTMLResponse(log, status_code=500)
    else:
        log = f"{TASK_MISSING} (cid: {connection_id})"
        logger.warning(log)
        return HTMLResponse(log, status_code=404)

    return HTMLResponse("Cancelled")


async def response_stream(request: Request) -> StreamingResponse:
    connection_id = str(request.query_params.get("connection_id"))
    logger.info(f"{STREAM_REQUESTED} (cid: {connection_id})")

    new_stream_state = StreamState()
    active_connections[connection_id] = new_stream_state
    logger.info(f"{STREAM_CREATED} (cid: {connection_id})")

    return StreamingResponse(
        event_stream(connection_id, new_stream_state),
        media_type="text/event-stream",
    )


async def error_stream(message: str) -> AsyncGenerator[str, None]:
    logger.error(f"{STREAM_FAILED} (message: {message})")
    yield f"event: error\ndata: {message}\n\n"
    yield "event: close\ndata: N/A\n\n"


async def process_prompt(prompt: str, state: StreamState) -> AsyncGenerator[str, None]:
    state.task = asyncio.current_task()

    try:
        for i in range(1, 11):
            if state.is_cancelled:
                logger.info(f"{TASK_CANCELED} (step: {i})")
                yield f"event: cancelled\ndata: Processing cancelled at step {i}\n\n"
                break
            message = f"[{i}] — {prompt}"
            logger.info(f"{TASK_CHUNK_STREAMED} (step: {i}) (message: {message})")
            yield f"event: response\ndata: <span class='message'>{message}</span><br>\n\n"
            await asyncio.sleep(0.3)  # Simulate processing time

        if not state.is_cancelled:
            logger.info(f"{TASK_COMPLETED} (cid: TBD)")
            yield "event: complete\ndata: Response complete\n\n"
    except asyncio.CancelledError:
        logger.info(f"{TASK_CANCELLED} (via CancelledError)")
        yield "event: cancelled\ndata: Task cancelled\n\n"
        raise
    finally:
        logger.info(f"{TASK_CLEARED} (cid: TBD)")
        state.task = None


async def event_stream(
    connection_id: str, state: StreamState
) -> AsyncGenerator[str, None]:
    try:
        logger.info(f"{STREAM_STARTED} (cid: {connection_id})")
        yield "event: connected\ndata: Connection established\n\n"

        while True:
            try:
                # Wait for events from the queue
                logger.info(f"{EVENT_AWAITED} (cid: {connection_id})")
                event = await state.queue.get()
                msg = f"{EVENT_RECEIVED} (cid: {connection_id}) (type: {event['type']})"
                logger.info(msg)

                if event["type"] == "prompt":
                    prompt = event["data"]
                    msg = f"{EVENT_PROCESSED} (cid: {connection_id})"
                    logger.info(msg)
                    async for message in process_prompt(prompt, state):
                        log = f"{EVENT_STREAMED} (cid: {connection_id}) (length: {len(message)})"
                        logger.info(log)
                        yield message

            except asyncio.CancelledError:
                logger.info(f"{STREAM_CANCELED} (cid: {connection_id})")
                yield "event: cancelled\ndata: Stream cancelled\n\n"
                break

    finally:
        if connection_id in active_connections:
            logger.info(f"{STREAM_CLOSED} (cid: {connection_id})")
            del active_connections[connection_id]
        yield "event: close\ndata: N/A\n\n"


routes = [
    Route(ROOT_PAGE, root_page),
    Route(SUBMIT_PROMPT, submit_prompt, methods=["POST"]),
    Route(RESPONSE_STREAM, response_stream, methods=["GET"]),
    Route(CANCEL_STREAM, cancel_stream, methods=["POST"]),
]
