"""File guide.

- Use: Turns retrieved chunks into bounded context text for prompts.
- Usage: Import ContextBuilder, and ContextBuilderConfig from
  openagentlab.rag.context.builder.
- Duties: Defines ContextBuilder, and ContextBuilderConfig and related helper logic.
- Depends on: Project modules: openagentlab.rag.models.
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

from openagentlab.rag.models import BuiltContext, RetrievedChunk

logger = logging.getLogger(__name__)


class ContextBuilderConfig(BaseModel):
    """Configuration for deterministic retrieved-context formatting."""

    max_tokens: int | None = Field(default=None, ge=1)


class ContextBuilder:
    """Format retrieved chunks into source-aware context for an LLM caller."""

    def __init__(self, *, max_tokens: int | None = None) -> None:
        self.config = ContextBuilderConfig(max_tokens=max_tokens)

    def build(self, retrieved_chunks: list[RetrievedChunk]) -> BuiltContext:
        if not retrieved_chunks:
            return BuiltContext(text="", sources=())

        sections: list[str] = []
        sources: list[dict[str, Any]] = []
        seen_chunk_ids: set[str] = set()
        used_tokens = 0
        source_number = 1

        for result in retrieved_chunks:
            chunk = result.chunk
            if chunk.id in seen_chunk_ids:
                continue

            chunk_tokens = chunk.token_count or len(chunk.text.split())
            if (
                self.config.max_tokens is not None
                and used_tokens + chunk_tokens > self.config.max_tokens
            ):
                break

            seen_chunk_ids.add(chunk.id)
            used_tokens += chunk_tokens
            source = self._source_record(source_number, result)
            sources.append(source)
            sections.append(self._format_source(source, chunk.text))
            source_number += 1

        context = BuiltContext(text="\n\n".join(sections), sources=tuple(sources))
        logger.info(
            "Context built",
            extra={"source_count": len(context.sources), "token_count": used_tokens},
        )
        return context

    def _source_record(
        self,
        source_number: int,
        result: RetrievedChunk,
    ) -> dict[str, Any]:
        chunk = result.chunk
        metadata = chunk.metadata
        return {
            "source_number": source_number,
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "source": metadata.get("source"),
            "filename": metadata.get("filename"),
            "file_type": metadata.get("file_type"),
            "page_number": metadata.get("page_number"),
            "chunk_index": chunk.chunk_index,
            "score": result.score,
        }

    @staticmethod
    def _format_source(source: dict[str, Any], text: str) -> str:
        lines = [f"[Source {source['source_number']}]"]
        if source.get("filename"):
            lines.append(f"File: {source['filename']}")
        elif source.get("source"):
            lines.append(f"Source: {source['source']}")

        if source.get("page_number") is not None:
            lines.append(f"Page: {source['page_number']}")

        lines.extend(["", text])
        return "\n".join(lines)
