from sqlalchemy import func
from sqlalchemy.orm import Session

from src.app.models.user_model import User
from src.app.services.ai_service import (
    generate_ai_response,
)


# ==================================================
# GET BUSINESS STATISTICS
# ==================================================

def get_business_statistics(
    db: Session,
) -> dict:

    # ----------------------------------------------
    # Total members
    # ----------------------------------------------

    total_members = (
        db.query(
            func.count(User.id)
        )
        .scalar()
    ) or 0

    # ----------------------------------------------
    # Paid members
    # ----------------------------------------------

    paid_members = (
        db.query(
            func.count(User.id)
        )
        .filter(
            User.is_paid_chandha.is_(True)
        )
        .scalar()
    ) or 0

    # ----------------------------------------------
    # Unpaid members
    # ----------------------------------------------

    unpaid_members = (
        db.query(
            func.count(User.id)
        )
        .filter(
            User.is_paid_chandha.is_(False)
        )
        .scalar()
    ) or 0

    # ----------------------------------------------
    # Payment percentage
    # ----------------------------------------------

    if total_members > 0:

        payment_percentage = (
            paid_members / total_members
        ) * 100

    else:

        payment_percentage = 0

    return {
        "total_members": total_members,
        "paid_members": paid_members,
        "unpaid_members": unpaid_members,
        "payment_percentage": round(
            payment_percentage,
            2,
        ),
    }


# ==================================================
# ASK AI BUSINESS QUESTION
# ==================================================

async def ask_business_question(
    db: Session,
    question: str,
) -> str:

    # ----------------------------------------------
    # 1. Get business data
    # ----------------------------------------------

    statistics = get_business_statistics(
        db
    )

    # ----------------------------------------------
    # 2. Build AI context
    # ----------------------------------------------

    context = f"""
Organization Business Statistics:

Total Members:
{statistics["total_members"]}

Paid Chandha Members:
{statistics["paid_members"]}

Unpaid Chandha Members:
{statistics["unpaid_members"]}

Chandha Payment Percentage:
{statistics["payment_percentage"]}%
"""

    # ----------------------------------------------
    # 3. AI system prompt
    # ----------------------------------------------

    system_prompt = """
You are an AI business assistant
for an organization.

Answer the user's question using
only the provided business data.

Rules:

1. Do not invent numbers.
2. Do not assume missing information.
3. Use the provided statistics accurately.
4. If the requested information is not
   available, clearly say so.
5. Keep the answer simple and professional.
6. You may explain relationships between
   the provided numbers.
"""

    # ----------------------------------------------
    # 4. Send data to AI
    # ----------------------------------------------

    response = await generate_ai_response(
        prompt=question,
        system_prompt=system_prompt,
        history=[
            {
                "role": "user",
                "content": context,
            }
        ],
    )

    return response