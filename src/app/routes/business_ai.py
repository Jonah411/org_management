
from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.schemas.ai import (
    BusinessAIQuestion,
)
from src.app.services.business_ai_service import (
    ask_business_question,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/business"
)
async def business_ai_endpoint(
    data: BusinessAIQuestion,
    db: Session = Depends(get_db),
):

    response = await ask_business_question(
        db=db,
        question=data.question,
    )

    return {
        "success": True,
        "question": data.question,
        "response": response,
    }

