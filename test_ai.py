from src.app.services.ai_service import generate_ai_response


result = generate_ai_response(
    prompt="Explain dependency injection.",
    system_prompt=(
        "You are an experienced FastAPI developer. "
        "Explain concepts clearly with practical examples."
    )
)

print(result)