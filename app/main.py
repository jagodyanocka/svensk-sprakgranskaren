from contextlib import asynccontextmanager
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.db import init_db
from app.gradio_app.gradio_app import theme, tutor


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health-check")
def health():
    return {"status": "ok"}


app = gr.mount_gradio_app(
    app,
    tutor,
    path="/",
    theme=theme,
    footer_links=[],
)
