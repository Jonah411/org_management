from fastapi import APIRouter, status

from src.app.schemas.ai_schema import (
    AIChatRequest,
    AIChatResponse,
    AIConversationHistoryResponse,
)
from src.app.services.ai_service import generate_ai_response
from src.app.services.ai_conversation_service import (
    delete_conversation,
    get_history,
    save_message,
)

from fastapi.responses import StreamingResponse
from src.app.services.ai_stream_service import stream_ai_response

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post(
    "/chat",
    response_model=AIChatResponse
)
def chat_with_ai(request: AIChatRequest):

    # 1. Get previous conversation from Redis
    history = get_history(
        request.conversation_id
    )

    # 2. Send history + current prompt to AI
    response = generate_ai_response(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        history=history
    )

    # 3. Save user message
    save_message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.prompt
    )

    # 4. Save AI response
    save_message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=response
    )

    return AIChatResponse(
        response=response
    )

@router.get(
    "/chat/{conversation_id}/history",
    response_model=AIConversationHistoryResponse
)
def get_chat_history(conversation_id: str):

    history = get_history(
        conversation_id
    )

    return AIConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=history
    )

@router.delete(
    "/chat/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_chat(conversation_id: str):

    delete_conversation(
        conversation_id
    )

    return None


@router.post("/chat/stream")
def stream_chat(request: AIChatRequest):

    history = get_history(
        request.conversation_id
    )

    def generate_stream():

        full_response = ""

        for chunk in stream_ai_response(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            history=history
        ):
            full_response += chunk

            yield chunk

        save_message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.prompt
        )

        save_message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=full_response
        )

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
    )