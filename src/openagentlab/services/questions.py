"""File guide.

- Use: Coordinates question answering through retrieval, context, and response
  generation services.
- Usage: Import QuestionAnsweringService and RAGQuestionAnsweringService from
  openagentlab.services.questions.
- Duties: Validates document scope, runs RAG retrieval, records workflow state,
  and delegates final answer generation.
- Depends on: Project modules: openagentlab.agent, openagentlab.core.exceptions,
  openagentlab.database.enums, openagentlab.rag, openagentlab.repositories, and
  openagentlab.services.documents.
"""

from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from fastapi import status

from openagentlab.agent.exceptions import AgentError
from openagentlab.agent.response_generator import ResponseGenerator
from openagentlab.core.exceptions import AppException
from openagentlab.database.enums import WorkflowExecutionStatus
from openagentlab.rag.context.builder import ContextBuilder
from openagentlab.rag.exceptions import RAGError
from openagentlab.rag.models import BuiltContext, RetrievedChunk
from openagentlab.rag.retrieval.retriever import Retriever
from openagentlab.repositories.workflow_execution import WorkflowExecutionRepository
from openagentlab.services.documents import DocumentService

QUESTION_WORKFLOW_NAME = "question_answering"


class QuestionAnsweringError(AppException):
    """Raised when the question-answering workflow fails safely."""

    def __init__(self, message: str = "Question answering failed.") -> None:
        super().__init__(
            message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="QUESTION_ANSWERING_FAILED",
        )


@dataclass(frozen=True)
class QuestionInput:
    question: str
    document_ids: list[UUID]


@dataclass(frozen=True)
class QuestionAnswer:
    answer: str
    workflow_id: UUID | None
    sources: tuple[dict[str, Any], ...]


class QuestionAnsweringService(Protocol):
    async def answer(self, question_input: QuestionInput) -> QuestionAnswer:
        """Answer a user question using the configured orchestration path."""


class RAGQuestionAnsweringService:
    """Question-answering facade over deterministic RAG and LLM response output."""

    def __init__(
        self,
        *,
        retriever: Retriever,
        context_builder: ContextBuilder,
        response_generator: ResponseGenerator,
        document_service: DocumentService,
        workflow_repository: WorkflowExecutionRepository | None = None,
        top_k: int = 5,
    ) -> None:
        self._retriever = retriever
        self._context_builder = context_builder
        self._response_generator = response_generator
        self._document_service = document_service
        self._workflow_repository = workflow_repository
        self._top_k = top_k

    async def answer(self, question_input: QuestionInput) -> QuestionAnswer:
        question = question_input.question.strip()
        workflow_id = await self._start_workflow(question, question_input.document_ids)

        try:
            if question_input.document_ids:
                await self._document_service.ensure_documents_exist(
                    question_input.document_ids,
                )

            context = self._retrieve_context(question, question_input.document_ids)
            answer = self._response_generator.generate_response(
                user_query=question,
                plan=[
                    "retrieve relevant indexed document context",
                    "generate a grounded answer from retrieved context",
                ],
                tool_name="rag.retrieve",
                tool_result=context.model_dump(mode="json"),
            )
        except AppException as exc:
            await self._mark_workflow_failed(workflow_id, exc.message)
            raise
        except (AgentError, RAGError) as exc:
            await self._mark_workflow_failed(
                workflow_id,
                "Question answering workflow failed.",
            )
            raise QuestionAnsweringError() from exc
        except Exception as exc:
            await self._mark_workflow_failed(
                workflow_id,
                "Question answering workflow failed.",
            )
            raise QuestionAnsweringError() from exc

        sources = context.sources
        await self._mark_workflow_completed(
            workflow_id,
            {"answer": answer, "sources": list(sources)},
        )
        return QuestionAnswer(answer=answer, workflow_id=workflow_id, sources=sources)

    def _retrieve_context(
        self,
        question: str,
        document_ids: list[UUID],
    ) -> BuiltContext:
        retrieved = self._retrieve_chunks(question, document_ids)
        return self._context_builder.build(retrieved)

    def _retrieve_chunks(
        self,
        question: str,
        document_ids: list[UUID],
    ) -> list[RetrievedChunk]:
        if not document_ids:
            return self._retriever.retrieve(question, top_k=self._top_k)

        retrieved: list[RetrievedChunk] = []
        for document_id in dict.fromkeys(document_ids):
            retrieved.extend(
                self._retriever.retrieve(
                    question,
                    top_k=self._top_k,
                    filters={"document_id": str(document_id)},
                )
            )

        return sorted(retrieved, key=lambda result: result.score, reverse=True)[
            : self._top_k
        ]

    async def _start_workflow(
        self,
        question: str,
        document_ids: list[UUID],
    ) -> UUID | None:
        if self._workflow_repository is None:
            return None

        workflow = await self._workflow_repository.create(
            workflow_name=QUESTION_WORKFLOW_NAME,
            status=WorkflowExecutionStatus.RUNNING,
            input_payload={
                "question": question,
                "document_ids": [str(document_id) for document_id in document_ids],
            },
        )
        return workflow.id

    async def _mark_workflow_completed(
        self,
        workflow_id: UUID | None,
        output_payload: dict[str, Any],
    ) -> None:
        if workflow_id is not None and self._workflow_repository is not None:
            await self._workflow_repository.complete(
                workflow_id,
                output_payload=output_payload,
            )

    async def _mark_workflow_failed(
        self,
        workflow_id: UUID | None,
        error_message: str,
    ) -> None:
        if workflow_id is not None and self._workflow_repository is not None:
            await self._workflow_repository.fail(
                workflow_id,
                error_message=error_message,
            )
