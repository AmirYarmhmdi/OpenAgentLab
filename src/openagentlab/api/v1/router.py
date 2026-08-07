from fastapi import APIRouter

from openagentlab.api.v1.endpoints import health

# This router collects every v1 endpoint module.
router = APIRouter()

# Health is the only v1 endpoint implemented in Phase 3.
router.include_router(health.router, tags=["health"])
