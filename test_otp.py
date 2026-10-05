from src.app.services.otp_service import (
    generate_otp,
    save_otp,
    get_otp,
)
from src.app.core.redis import redis_client


phone_number = "9876543210"

otp = generate_otp()

save_otp(phone_number, otp)

print("Generated OTP:", otp)
print("Saved OTP:", get_otp(phone_number))

redis_key = f"otp:{phone_number}"

print("TTL:", redis_client.ttl(redis_key))