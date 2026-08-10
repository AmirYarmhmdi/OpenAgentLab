"""File guide.

- Use: Creates the FastAPI application and wires startup, logging, routers, and
  errors.
- Usage: Import create_app, create_lifespan, and main from openagentlab.main.
- Duties: Defines create_app, create_lifespan, and main and related helper logic.
- Depends on: Project modules: openagentlab.api.router, openagentlab.core.config,
  openagentlab.core.exceptions, and openagentlab.core.logging.
"""

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from openagentlab.api.router import router as api_router
from openagentlab.core.config import Settings, get_settings
from openagentlab.core.exceptions import register_exception_handlers
from openagentlab.core.logging import configure_logging

logger = logging.getLogger(__name__)


# This creates the startup and shutdown behavior for the FastAPI app.
def create_lifespan(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Log basic startup information without exposing secrets.
        logger.info(
            "Starting %s version %s in %s environment",
            settings.APP_NAME,
            settings.APP_VERSION,
            settings.ENVIRONMENT,
        )
        yield
        logger.info("Stopping %s", settings.APP_NAME)

    return lifespan


# This builds and configures the FastAPI application.
def create_app() -> FastAPI:
    # Load settings once and use them to configure the app.
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)

    # Create the FastAPI app with project name, version, debug mode, and lifespan.
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=create_lifespan(settings),
    )

    # Store settings on the app and connect routers and exception handlers.
    app.state.settings = settings
    app.include_router(api_router)
    register_exception_handlers(app)

    # This is a minimal root endpoint for a quick running check.
    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": settings.APP_NAME,
            "status": "running",
        }

    logger.info(
        "Application initialized: name=%s version=%s environment=%s",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )

    return app


# This is the app object used by Uvicorn.
app = create_app()


# This is a small command-line helper if this file is run directly.
def main() -> None:
    settings = get_settings()
    print(
        f"{settings.APP_NAME} backend is ready. "
        f"Run: uvicorn openagentlab.main:app --reload"
    )


if __name__ == "__main__":
    main()
