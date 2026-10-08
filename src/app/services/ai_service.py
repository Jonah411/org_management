from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from src.app.core.exceptions import AIServiceException
from src.app.core.security import settings


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)


async def generate_ai_response(
    prompt: str,
    system_prompt: str,
    history: list,
) -> str:

    try:

        input_messages = [
            *history,
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = await client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=system_prompt,
            input=input_messages,
        )

        return response.output_text

    except AuthenticationError as exc:

        raise AIServiceException(
            "AI authentication failed."
        ) from exc

    except RateLimitError as exc:

        raise AIServiceException(
            "AI service rate limit or credit limit reached."
        ) from exc

    except APIConnectionError as exc:

        raise AIServiceException(
            "Unable to connect to AI service."
        ) from exc

    except APIStatusError as exc:

        raise AIServiceException(
            "AI service is temporarily unavailable."
        ) from exc