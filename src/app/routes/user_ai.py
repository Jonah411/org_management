from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.schemas.ai import UserAIQuestion
from src.app.services.user_ai_service import (
    ask_user_data,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/user-data"
)
async def ask_user_data_endpoint(
    data: UserAIQuestion,
    db: Session = Depends(get_db),
):

    response = await ask_user_data(
        db=db,
        user_id=data.user_id,
        question=data.question,
    )

    if response is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return {
        "success": True,
        "user_id": data.user_id,
        "question": data.question,
        "response": response,
    }