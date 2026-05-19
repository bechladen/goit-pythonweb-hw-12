from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.api.auth import router as auth_router
from src.api.contacts import router as contacts_router
from src.api.users import router as users_router
from src.database import init_db
from src.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Contacts API",
        version="0.1.0",
        description="REST API для зберігання та управління контактами.",
    )

    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"error": "Too many requests. Please try again later."},
        )

    app.include_router(auth_router, prefix="/api")
    app.include_router(contacts_router, prefix="/api")
    app.include_router(users_router, prefix="/api")

    @app.on_event("startup")
    async def on_startup() -> None:
        if settings.AUTO_CREATE_TABLES:
            # Для навчального проєкту цього достатньо.
            # У реальних проєктах краще вимикати це й використовувати міграції (Alembic).
            await init_db()

    return app


app = create_app()

