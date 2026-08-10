"""File guide.

- Use: Contains unit tests for context builder behavior.
- Usage: Run this file with pytest when checking related behavior.
- Duties: Builds test data, calls the public API, and checks expected results.
- Depends on: Project modules: openagentlab.rag.context.builder, and
  openagentlab.rag.models.
"""

from openagentlab.rag.context.builder import ContextBuilder
from openagentlab.rag.models import Chunk, RetrievedChunk


def retrieved(chunk_id: str, text: str, page_number: int | None) -> RetrievedChunk:
    return RetrievedChunk(
        chunk=Chunk(
            id=chunk_id,
            document_id="doc-1",
            text=text,
            chunk_index=0,
            metadata={
                "filename": "report.pdf",
                "file_type": "pdf",
                "page_number": page_number,
                "source": "/tmp/report.pdf",
            },
            token_count=len(text.split()),
        ),
        score=0.9,
    )


def test_context_builder_formats_sources_and_pages_in_order() -> None:
    context = ContextBuilder().build(
        [
            retrieved("chunk-1", "alpha text", 12),
            retrieved("chunk-2", "beta text", None),
        ]
    )

    assert "[Source 1]" in context.text
    assert "File: report.pdf" in context.text
    assert "Page: 12" in context.text
    assert context.text.index("alpha text") < context.text.index("beta text")
    assert context.sources[0]["page_number"] == 12


def test_context_builder_returns_empty_context_for_empty_results() -> None:
    context = ContextBuilder().build([])

    assert context.text == ""
    assert context.sources == ()


def test_context_builder_deduplicates_chunks_and_respects_token_budget() -> None:
    first = retrieved("chunk-1", "alpha beta", 1)
    duplicate = retrieved("chunk-1", "alpha beta", 1)
    second = retrieved("chunk-2", "gamma delta epsilon", 2)

    context = ContextBuilder(max_tokens=2).build([first, duplicate, second])

    assert context.text.count("[Source") == 1
    assert "alpha beta" in context.text
    assert "gamma delta epsilon" not in context.text
