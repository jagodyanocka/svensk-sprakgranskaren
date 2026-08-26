import os
from collections.abc import Iterator
from pathlib import Path

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.db import save_interaction

LLM_BASE_URL = os.environ.get("LLM_URL")
LLM_MODEL = os.environ.get("LLM_MODEL")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "ollama")
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "tutor.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()

if not LLM_BASE_URL or not LLM_MODEL:
    raise RuntimeError(
        "LLM_URL and LLM_MODEL must be set"
    )

ollama_client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


def react_to_user_poor_swedish(
    message: str,
    language: str,
) -> Iterator[str]:
    system_prompt = f"""
    /no_think

    {SYSTEM_PROMPT}

    The selected language is: {language}.
    The user's message is written in {language}.
    Your entire response must be in {language}.
    Keep the response concise.
    """

    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            role="system",
            content=system_prompt,
        ),
        ChatCompletionUserMessageParam(
            role="user",
            content=message,
        ),
    ]

    stream = ollama_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        stream=True,
        max_tokens=200,
        temperature=0.5,
        reasoning_effort="low",
    )

    response = ""

    for chunk in stream:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            response += content
            yield response

    if not response:
        yield "Sorry, I couldn't generate a response. Please try again."
        return

    save_interaction(
        language=language,
        input_text=message,
        output_text=response,
    )

