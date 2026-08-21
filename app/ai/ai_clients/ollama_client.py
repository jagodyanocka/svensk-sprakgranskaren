from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionMessageParam, ChatCompletionChunk

OLLAMA_BASE_URL = "http://localhost:11434/v1"
from pathlib import Path

OLLAMA_MODEL = "gpt-oss:20b-cloud"
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "tutor.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text()

ollama_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

def react_to_user_poor_swedish(message: str, history: list) -> str:

    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            role="system",
            content=SYSTEM_PROMPT
        ),

        ChatCompletionUserMessageParam(
            role="user",
            content=message
        )
    ]
    stream = ollama_client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        stream=True,
        reasoning_effort="low",
        max_tokens=200
    )
    responses = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            responses += content

    if not responses:
        return "Sorry, I couldn't generate a response. Please try again."

    return responses

