"""File guide.

- Use: Builds the version 1 API router and includes endpoint modules.
- Usage: Import openagentlab.api.v1.router when this module is needed.
- Duties: Keeps this small package area organized for imports.
- Depends on: Project modules: openagentlab.api.v1.endpoints.
"""

from fastapi import APIRouter

from openagentlab.api.v1.endpoints import documents, health, questions, workflows

# This router collects every v1 endpoint module.
router = APIRouter()

# Health is the only v1 endpoint implemented in Phase 3.
router.include_router(health.router, tags=["health"])
router.include_router(documents.router, tags=["documents"])
router.include_router(questions.router, tags=["questions"])
router.include_router(workflows.router, tags=["workflows"])
