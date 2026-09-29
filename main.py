"""Run with: python -m uvicorn main:app --host 127.0.0.1 --port 8000"""

# Dispatch direct Python execution before loading third-party API dependencies.
# ruff: noqa: E402
if __name__ == "__main__":
    from run import main as launch_application

    raise SystemExit(launch_application())

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from config import get_settings
from routes import router


class BodyLimit:
    """Bound complete ASGI bodies, including chunked requests, before JSON parsing."""

    def __init__(self, app: ASGIApp, limit: int = 8_000_000):
        self.app, self.limit = app, limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        messages, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > self.limit:
                response = JSONResponse({"detail": "Request is too large (maximum 8 MB)."}, status_code=413)
                return await response(scope, receive, send)
            messages.append(message)
            if not message.get("more_body", False):
                break
        index = 0

        async def replay():
            nonlocal index
            if index < len(messages):
                message = messages[index]
                index += 1
                return message
            return await receive()

        await self.app(scope, replay, send)


app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description="Local legal drafting workspace. All output requires professional review.",
)
app.add_middleware(BodyLimit)
app.include_router(router)


@app.middleware("http")
async def private_responses(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Pydantic's default error includes the submitted input. Do not echo legal text or logos.
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]} for error in exc.errors()
            ]
        },
    )


@app.get("/")
def home():
    return {"name": "LegalEase", "version": "1.0.0", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    s = get_settings()
    return {
        "status": "ok",
        "provider": s.ai_provider,
        "model": s.gemini_model if s.ai_provider == "gemini" else "offline-template",
        "configured": s.ai_provider == "demo" or bool(s.gemini_api_key.get_secret_value()),
    }
