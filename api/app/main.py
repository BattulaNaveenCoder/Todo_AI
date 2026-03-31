"""FastAPI application factory and configuration."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    application = FastAPI(
        title="Todo AI API",
        version="0.1.0",
        description="A single-user Todo application with category support",
    )

    # CORS — allow Vite dev server during development
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @application.get("/", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Return API health status."""
        return {"status": "healthy"}

    # Phase 1: register Todo CRUD router
    from app.routes.todo_router import router as todo_router

    application.include_router(todo_router, prefix="/api/todos", tags=["todos"])

    # Phase 3 (categories) router will be added here
    # application.include_router(category_router, prefix="/api/categories", tags=["categories"])

    logger.info("Todo AI API initialized")
    return application


app = create_app()
