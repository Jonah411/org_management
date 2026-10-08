import json

from sqlalchemy.orm import Session

from src.app.core.redis import redis_client
from src.app.models.conversation import (
    ConversationMessage,
)
from src.app.services.ai_service import (
    generate_ai_response,
)


MAX_MESSAGES = 10
REDIS_TTL = 3600


# ==================================================
# REDIS
# ==================================================

def get_conversation_key(
    conversation_id: str,
) -> str:

    return f"ai:conversation:{conversation_id}"


def get_history(
    conversation_id: str,
) -> list:

    key = get_conversation_key(
        conversation_id
    )

    history = redis_client.get(key)

    if not history:
        return []

    return json.loads(history)


def save_message(
    conversation_id: str,
    role: str,
    content: str,
):

    key = get_conversation_key(
        conversation_id
    )

    history = get_history(
        conversation_id
    )

    history.append(
        {
            "role": role,
            "content": content,
        }
    )

    history = history[-MAX_MESSAGES:]

    redis_client.set(
        key,
        json.dumps(history),
        ex=REDIS_TTL,
    )


def delete_conversation(
    conversation_id: str,
) -> bool:

    key = get_conversation_key(
        conversation_id
    )

    deleted = redis_client.delete(key)

    return deleted > 0


# ==================================================
# POSTGRESQL
# ==================================================

def save_message_to_db(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
):

    message = ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_history(
    db: Session,
    conversation_id: str,
):

    return (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.conversation_id
            == conversation_id
        )
        .order_by(
            ConversationMessage.created_at.asc()
        )
        .all()
    )


# ==================================================
# AI CHAT
# ==================================================

async def chat(
    db: Session,
    conversation_id: str,
    message: str,
):

    # --------------------------------------------------
    # 1. Get previous conversation history
    # --------------------------------------------------

    history = get_history(
        conversation_id
    )

    # --------------------------------------------------
    # 2. System prompt
    # --------------------------------------------------

    system_prompt = """
You are a helpful AI assistant.

Answer the user's questions clearly and accurately.

Use the conversation history to understand
the context of previous messages.

If you do not know something, clearly say
that you do not know instead of making up
information.
"""

    # --------------------------------------------------
    # 3. Generate AI response
    # --------------------------------------------------

    ai_response = await generate_ai_response(
        prompt=message,
        system_prompt=system_prompt,
        history=history,
    )

    # --------------------------------------------------
    # 4. Save user message → Redis
    # --------------------------------------------------

    save_message(
        conversation_id=conversation_id,
        role="user",
        content=message,
    )

    # --------------------------------------------------
    # 5. Save user message → PostgreSQL
    # --------------------------------------------------

    save_message_to_db(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message,
    )

    # --------------------------------------------------
    # 6. Save AI response → Redis
    # --------------------------------------------------

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response,
    )

    # --------------------------------------------------
    # 7. Save AI response → PostgreSQL
    # --------------------------------------------------

    save_message_to_db(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response,
    )

    # --------------------------------------------------
    # 8. Return AI response
    # --------------------------------------------------

    return ai_response

