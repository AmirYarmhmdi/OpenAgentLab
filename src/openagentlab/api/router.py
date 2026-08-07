from fastapi import APIRouter

from openagentlab.api.v1.router import router as v1_router
from openagentlab.core.config import get_settings

# Load settings so the API prefix can come from one central place.
settings = get_settings()

# This is the top-level API router for the whole backend.
router = APIRouter()

# This mounts version 1 routes under the configured API prefix.
router.include_router(v1_router, prefix=settings.API_V1_PREFIX)
