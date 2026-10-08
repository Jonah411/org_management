from fastapi import APIRouter

from src.app.schemas.ai_analysis_schema import AIAnalysisResult
from src.app.services.ai_structured_service import analyze_with_ai


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post(
    "/analyze",
    response_model=AIAnalysisResult
)
def analyze_topic(prompt: str):

    return analyze_with_ai(prompt)