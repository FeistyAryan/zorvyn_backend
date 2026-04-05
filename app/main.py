import time
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.limiter import limiter
from app.core.middlewares.correlation_id import CorrelationIDMiddleware
from app.core.exceptions.base import AppBaseException, app_exception_handler

setup_logging()

app = FastAPI(
    title="Zorvyn-Backend",
    description="Production-ready API with RBAC, Logging, and Rate Limiting",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware) 
app.add_middleware(CorrelationIDMiddleware) 

app.add_exception_handler(AppBaseException, app_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "version": "1.0.0"
    }
