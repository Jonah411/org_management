from src.app.core.redis import redis_client


print("Redis connected:", redis_client.ping())