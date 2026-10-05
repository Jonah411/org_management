from src.app.core.security import (
    get_twilio_client,
    get_whatsapp_from,
    get_whatsapp_template_sid,
)


def send_whatsapp_otp(
    phone_number: str,
    otp: str,
) -> str:

    client = get_twilio_client()

    message = client.messages.create(
        from_=get_whatsapp_from(),
        content_sid=get_whatsapp_template_sid(),
        content_variables=f'{{"1":"{otp}"}}',
        to=f"whatsapp:+91{phone_number}",
    )

    return message.sid