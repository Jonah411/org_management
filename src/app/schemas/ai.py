from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):

    conversation_id: str
    message: str


class ConversationMessageResponse(BaseModel):

    id: int
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class UserAIQuestion(BaseModel):

    user_id: int
    question: str

class BusinessAIQuestion(BaseModel):

    question: str