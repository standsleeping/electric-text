import os
import asyncio
import uuid
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, StreamingResponse
from starlette.requests import Request
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


@app.route("/submit-prompt", methods=["POST"])
async def submit_prompt(request: Request):
    form = await request.form()
    prompt = form.get("prompt")
    prompt_id = str(uuid.uuid4())

    response_area = f"""
    <div id="response-area" hx-ext="sse" sse-connect="/response-stream?prompt_id={prompt_id}" sse-swap="SomeEventName">
        (Generating response for prompt: {prompt})
    </div>
    """

    return HTMLResponse(response_area)


@app.route("/response-stream", methods=["GET"])
async def response_stream(request):
    prompt_id = request.query_params.get("prompt_id")
    return StreamingResponse(event_stream(prompt_id), media_type="text/event-stream")


async def event_stream(prompt_id):
    while True:
        data = f"event: SomeEventName\ndata: <div style='font-family: monospace;'>Prompt ID {prompt_id}: ({uuid.uuid4()})</div>\n\n"
        yield data
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
