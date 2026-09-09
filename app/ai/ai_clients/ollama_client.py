import os
from collections.abc import Iterator
from pathlib import Path

import boto3
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.db import save_interaction

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()
LLM_BASE_URL = os.environ.get("LLM_URL")
LLM_MODEL = os.environ.get("LLM_MODEL")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "ollama")
AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "tutor.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()

if not LLM_MODEL:
    raise RuntimeError("LLM_MODEL must be set")

if LLM_PROVIDER == "ollama" and not LLM_BASE_URL:
    raise RuntimeError("LLM_URL must be set when LLM_PROVIDER=ollama")

if LLM_PROVIDER == "bedrock" and not LLM_API_KEY:
    raise RuntimeError("LLM_API_KEY must be set when LLM_PROVIDER=bedrock")

_openai_client: OpenAI | None = None
if LLM_PROVIDER == "ollama":
    _openai_client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


def _tutor_system_prompt(language: str) -> str:
    prefix = "/no_think\n\n" if LLM_PROVIDER == "ollama" else ""
    return f"""
    {prefix}{SYSTEM_PROMPT}

    The selected language is: {language}.
    The user's message is written in {language}.
    Your entire response must be in {language}.
    Keep the response concise.
    """


def _stream_ollama(message: str, language: str) -> Iterator[str]:
    assert _openai_client is not None

    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            role="system",
            content=_tutor_system_prompt(language),
        ),
        ChatCompletionUserMessageParam(
            role="user",
            content=message,
        ),
    ]

    stream = _openai_client.chat.completions.create(
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


def _stream_bedrock(message: str, language: str) -> Iterator[str]:
    # Bedrock API keys are read from this env var by botocore.
    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = LLM_API_KEY

    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    stream = client.converse_stream(
        modelId=LLM_MODEL,
        system=[{"text": _tutor_system_prompt(language)}],
        messages=[
            {
                "role": "user",
                "content": [{"text": message}],
            }
        ],
        inferenceConfig={
            "maxTokens": 200,
            "temperature": 0.5,
        },
    )

    response = ""
    for event in stream.get("stream", []):
        delta = event.get("contentBlockDelta", {}).get("delta", {})
        text = delta.get("text")
        if text:
            response += text
            yield response

    if not response:
        yield "Sorry, I couldn't generate a response. Please try again."


def react_to_user_poor_swedish(
    message: str,
    language: str,
) -> Iterator[str]:
    if LLM_PROVIDER == "bedrock":
        stream = _stream_bedrock(message, language)
    elif LLM_PROVIDER == "ollama":
        stream = _stream_ollama(message, language)
    else:
        raise RuntimeError(
            f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. Use 'ollama' or 'bedrock'."
        )

    response = ""
    for partial in stream:
        response = partial
        yield partial

    if response:
        save_interaction(
            language=language,
            input_text=message,
            output_text=response,
        )
