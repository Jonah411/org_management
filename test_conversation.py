from src.app.services.ai_conversation_service import (
    get_history,
    save_message,
)


conversation_id = "jonah-001"


save_message(
    conversation_id,
    "user",
    "My name is Jonah."
)

save_message(
    conversation_id,
    "assistant",
    "Nice to meet you, Jonah!"
)


history = get_history(conversation_id)

print(history)