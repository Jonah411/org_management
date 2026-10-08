
from sqlalchemy.orm import Session

from src.app.models.user_model import User
from src.app.services.ai_service import (
    generate_ai_response,
)


# ==================================================
# GET USER FROM POSTGRESQL
# ==================================================

def get_user_for_ai(
    db: Session,
    user_id: int,
) -> User | None:

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    return user


# ==================================================
# BUILD AI CONTEXT
# ==================================================

def build_user_context(
    user: User,
) -> str:

    return f"""
User Information:

First Name: {user.first_name}
Last Name: {user.last_name or "Not provided"}
Age: {user.age}
Gender: {user.gender}
Qualification: {user.qualification}
Occupation: {user.occupation}
Date of Birth: {user.dob}
Married Status: {user.married_status}
Marriage Date: {user.marriage_date or "Not applicable"}
Chandha Paid: {"Yes" if user.is_paid_chandha else "No"}
Address: {user.address}
"""


# ==================================================
# ASK AI USING USER DATA
# ==================================================

async def ask_user_data(
    db: Session,
    user_id: int,
    question: str,
) -> str | None:

    # 1. Get user from PostgreSQL
    user = get_user_for_ai(
        db=db,
        user_id=user_id,
    )

    if not user:
        return None

    # 2. Convert PostgreSQL data into AI context
    context = build_user_context(
        user
    )

    # 3. System prompt
    system_prompt = """
You are a helpful AI assistant.

Answer the user's question using
only the provided user information.

Do not invent or assume information.

If the requested information is not
available in the provided user data,
clearly say that the information
is not available.
"""

    # 4. Send PostgreSQL data to AI
    ai_response = await generate_ai_response(
        prompt=question,
        system_prompt=system_prompt,
        history=[
            {
                "role": "user",
                "content": context,
            }
        ],
    )

    return ai_response

