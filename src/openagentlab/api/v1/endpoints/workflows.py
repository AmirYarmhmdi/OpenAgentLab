"""File guide.

- Use: Serves workflow status API endpoints.
- Usage: Included by openagentlab.api.v1.router.
- Duties: Delegates workflow state lookup to services and returns public schemas.
- Depends on: External packages: fastapi. Project modules:
  openagentlab.api.dependencies, openagentlab.schemas.workflows, and
  openagentlab.services.workflows.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from openagentlab.api.dependencies import get_workflow_status_service
from openagentlab.schemas.workflows import WorkflowStatusResponse
from openagentlab.services.workflows import WorkflowStatusService

router = APIRouter(prefix="/workflows")


@router.get(
    "/{workflow_id}",
    response_model=WorkflowStatusResponse,
    summary="Get workflow status",
)
async def get_workflow_status(
    workflow_id: UUID,
    workflow_service: Annotated[
        WorkflowStatusService,
        Depends(get_workflow_status_service),
    ],
) -> WorkflowStatusResponse:
    workflow = await workflow_service.get_workflow_status(workflow_id)
    return WorkflowStatusResponse(
        workflow_id=workflow.workflow_id,
        status=workflow.status,
        result=workflow.result,
        error=workflow.error,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        started_at=workflow.started_at,
        finished_at=workflow.finished_at,
    )
