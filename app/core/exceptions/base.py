from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse

class AppBaseException(Exception):
    """Base class for all app-specific exceptions."""
    def __init__(
        self, 
        message: str, 
        status_code: int = 400, 
        headers: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.headers = headers
        super().__init__(self.message)

async def app_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "status": "error",
            "correlation_id": getattr(request.state, "correlation_id", None)
        },
        headers=exc.headers
    )
