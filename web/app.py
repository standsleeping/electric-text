import os
import asyncio
import uuid
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, StreamingResponse
from string import Template
import uvicorn


def get_template(template_name="index.html"):
    index_file_path = os.path.join(os.path.dirname(__file__), "views", template_name)
    with open(index_file_path, "r") as file:
        return file.read()


def render_template(template_name, data):
    html_template = get_template(template_name)
    template = Template(html_template)
    rendered_html = template.substitute(data)
    return rendered_html


app = Starlette()


@app.route("/")
async def homepage(request):
    data = {
        "title": "Home",
        "name": "Ryan",
    }
    rendered_html = render_template("index.html", data)
    return HTMLResponse(rendered_html)


@app.route("/events", methods=["GET"])
async def sse_endpoint(request):
    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def event_stream():
    while True:
        data = f"event: SomeEventName\ndata: <div style='font-family: monospace;'>({uuid.uuid4()})</div>\n\n"
        yield data
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
