from src.app.core.security import hash_password


password = "MyPassword123"

hashed_password = hash_password(password)

print("Password:", password)
print("Hash:", hashed_password)