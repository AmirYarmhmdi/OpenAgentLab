"""File guide.

- Use: Serves the health-check endpoint for the API.
- Usage: Import health_check from openagentlab.api.v1.endpoints.health.
- Duties: Defines health_check and related helper logic.
- Depends on: Project modules: openagentlab.core.config, and
  openagentlab.schemas.health.
"""

from fastapi import APIRouter

from openagentlab.core.config import get_settings
from openagentlab.schemas.health import HealthResponse

# This router holds the health endpoint routes.
router = APIRouter()


# This endpoint lets callers check that the backend is running.
@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    # Read settings so the response uses the configured app identity.
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )
