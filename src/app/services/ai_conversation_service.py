import json

from src.app.core.redis import redis_client

MAX_MESSAGES = 2

def get_conversation_key(conversation_id: str) -> str:
    return f"ai:conversation:{conversation_id}"


def get_history(conversation_id: str) -> list:
    key = get_conversation_key(conversation_id)

    history = redis_client.get(key)

    if not history:
        return []

    return json.loads(history)


def save_message(
    conversation_id: str,
    role: str,
    content: str
):
    key = get_conversation_key(conversation_id)

    history = get_history(conversation_id)

    history.append(
        {
            "role": role,
            "content": content
        }
    )

    # Keep only the latest messages
    history = history[-MAX_MESSAGES:]

    redis_client.set(
        key,
        json.dumps(history),
        ex=3600
    )

def delete_conversation(conversation_id: str) -> bool:
    key = get_conversation_key(conversation_id)

    deleted = redis_client.delete(key)

    return deleted > 0