import uuid
import time
from fastapi import Request
from starlette.types import ASGIApp, Scope, Receive, Send

from app.core.logging import correlation_id_ctx

class CorrelationIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        token = correlation_id_ctx.set(correlation_id)
        
        scope["correlation_id"] = correlation_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"X-Correlation-ID"] = correlation_id.encode()
                message["headers"] = list(headers.items())
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            correlation_id_ctx.reset(token)
