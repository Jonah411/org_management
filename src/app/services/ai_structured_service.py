from openai import OpenAI

from src.app.core.exceptions import AIServiceException
from src.app.core.security import settings
from src.app.schemas.ai_analysis_schema import AIAnalysisResult


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def analyze_with_ai(prompt: str) -> AIAnalysisResult:

    try:

        response = client.responses.parse(
            model="gpt-5-mini",
            instructions=(
                "You are a technical expert. "
                "Analyze the user's topic and return "
                "clear and concise structured information."
            ),
            input=prompt,
            text_format=AIAnalysisResult
        )

        return response.output_parsed

    except Exception as exc:
        raise AIServiceException(
            "Unable to generate structured AI response."
        ) from exc