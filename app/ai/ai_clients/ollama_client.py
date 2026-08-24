from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionMessageParam, ChatCompletionChunk

OLLAMA_BASE_URL = "http://localhost:11434/v1"
from pathlib import Path

OLLAMA_MODEL = "gpt-oss:20b-cloud"
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "tutor.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()

ollama_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

from collections.abc import Iterator

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)


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
        model=OLLAMA_MODEL,
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

