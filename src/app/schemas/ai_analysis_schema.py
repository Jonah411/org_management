from pydantic import BaseModel


class AIAnalysisResult(BaseModel):
    title: str
    summary: str
    difficulty: str
    topics: list[str]