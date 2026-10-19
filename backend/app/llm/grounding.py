
from app.models.chunk import DocumentChunk
from app.schemas.answer import AnswerResponse, Citation


def build_evidence_answer(
    question: str,
    chunks: list[DocumentChunk],
    min_score: float = 0.10,
) -> AnswerResponse:
    """Build an evidence-based response from retrieved chunks."""

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not 0.0 <= min_score <= 1.0:
        raise ValueError("min_score must be between 0 and 1")

    supported_chunks = [
        chunk
        for chunk in chunks
        if getattr(chunk, "score", 0.0) >= min_score
    ]

    if not supported_chunks:
        return AnswerResponse(
            question=question,
            answer=(
                "I could not find sufficiently relevant evidence "
                "in the provided documents to answer this question."
            ),
            citations=[],
            confidence=0.0,
        )

    evidence = "\n\n".join(
        f"[{index}] {chunk.text}"
        for index, chunk in enumerate(supported_chunks, start=1)
    )

    citations = [
        Citation(
            source=chunk.source,
            page_number=chunk.page_number,
            chunk_id=chunk.chunk_id,
        )
        for chunk in supported_chunks
    ]

    return AnswerResponse(
        question=question,
        answer=(
            "Relevant evidence was retrieved from the provided "
            f"documents:\n\n{evidence}"
        ),
        citations=citations,
        confidence=min(
            1.0,
            sum(getattr(chunk, "score", 0.0) for chunk in supported_chunks)
            / len(supported_chunks),
        ),
    )
