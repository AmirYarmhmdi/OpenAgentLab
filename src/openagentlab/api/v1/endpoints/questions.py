"""File guide.

- Use: Serves question-answering API endpoints.
- Usage: Included by openagentlab.api.v1.router.
- Duties: Validates question requests, delegates retrieval/orchestration to
  services, and returns stable answer schemas.
- Depends on: External packages: fastapi. Project modules:
  openagentlab.api.dependencies, openagentlab.schemas.questions, and
  openagentlab.services.questions.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from openagentlab.api.dependencies import get_question_answering_service
from openagentlab.schemas.questions import QuestionRequest, QuestionResponse
from openagentlab.services.questions import QuestionAnsweringService, QuestionInput

router = APIRouter(prefix="/questions")


@router.post(
    "",
    response_model=QuestionResponse,
    summary="Ask question",
)
async def ask_question(
    request: QuestionRequest,
    question_service: Annotated[
        QuestionAnsweringService,
        Depends(get_question_answering_service),
    ],
) -> QuestionResponse:
    answer = await question_service.answer(
        QuestionInput(
            question=request.question,
            document_ids=request.document_ids,
        )
    )
    return QuestionResponse(
        answer=answer.answer,
        workflow_id=answer.workflow_id,
        sources=answer.sources,
    )
