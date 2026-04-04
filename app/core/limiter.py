from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from app.core.config import settings

def custom_key_func(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user_{user_id}"
    return get_remote_address(request)

limiter = Limiter(
    key_func=custom_key_func,
    storage_uri=settings.REDIS_URL
)