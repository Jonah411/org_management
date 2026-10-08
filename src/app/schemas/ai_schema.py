from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):

    conversation_id: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    system_prompt: str = Field(
        default=(
            "You are a helpful AI assistant. "
            "Give clear, accurate, and easy-to-understand answers."
        ),
        min_length=1,
        max_length=3000
    )

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


class AIChatResponse(BaseModel):
    response: str

class AIMessage(BaseModel):
    role: str
    content: str


class AIConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[AIMessage]