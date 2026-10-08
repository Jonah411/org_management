from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from src.app.core.exceptions import AIServiceException
from src.app.core.security import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

def stream_ai_response(
    prompt: str,
    system_prompt: str,
    history: list
):

    input_messages = history + [
        {
            "role": "user",
            "content": prompt
        }
    ]

    stream = client.responses.create(
        model="gpt-5-mini",
        instructions=system_prompt,
        input=input_messages,
        stream=True
    )

    for event in stream:

        if event.type == "response.output_text.delta":
            yield event.delta

