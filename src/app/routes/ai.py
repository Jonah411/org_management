from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from src.app.core.database import get_db

from src.app.schemas.ai import (
    ChatRequest,
    ConversationMessageResponse,
)

from src.app.services.conversation_service import (
    chat,
    get_conversation_history,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ==================================================
# POST /ai/chat
# ==================================================

@router.post("/chat")
async def chat_endpoint(
    data: ChatRequest,
    db: Session = Depends(get_db),
):

    response = await chat(
        db=db,
        conversation_id=data.conversation_id,
        message=data.message,
    )

    return {
        "success": True,
        "conversation_id": data.conversation_id,
        "response": response,
    }


# ==================================================
# GET /ai/conversations/{conversation_id}
# ==================================================

@router.get(
    "/conversations/{conversation_id}",
    response_model=list[
        ConversationMessageResponse
    ],
)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):

    return get_conversation_history(
        db=db,
        conversation_id=conversation_id,
    )