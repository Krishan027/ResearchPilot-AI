
import pytest

from app.llm.grounding import build_evidence_answer
from app.models.chunk import DocumentChunk


@pytest.fixture
def relevant_chunks():
    return [
        DocumentChunk(
            chunk_id="chunk-1",
            source="rag_guide.pdf",
            page_number=2,
            chunk_index=0,
            text=(
                "Retrieval Augmented Generation retrieves relevant "
                "documents before generating an answer."
            ),
            score=0.85,
        ),
        DocumentChunk(
            chunk_id="chunk-2",
            source="rag_guide.pdf",
            page_number=3,
            chunk_index=1,
            text=(
                "RAG can ground language model responses in "
                "external evidence."
            ),
            score=0.70,
        ),
    ]


def test_answer_contains_evidence_and_citations(relevant_chunks):
    response = build_evidence_answer(
        question="What is RAG?",
        chunks=relevant_chunks,
    )

    assert len(response.citations) == 2
    assert response.citations[0].source == "rag_guide.pdf"
    assert response.citations[0].page_number == 2
    assert "Retrieval Augmented Generation" in response.answer


def test_low_score_chunks_are_excluded(relevant_chunks):
    response = build_evidence_answer(
        question="What is RAG?",
        chunks=relevant_chunks,
        min_score=0.80,
    )

    assert len(response.citations) == 1
    assert response.citations[0].chunk_id == "chunk-1"


def test_no_evidence_returns_fallback(relevant_chunks):
    response = build_evidence_answer(
        question="Who won a fictional tournament?",
        chunks=relevant_chunks,
        min_score=0.99,
    )

    assert response.citations == []
    assert response.confidence == 0.0
    assert "could not find sufficiently relevant evidence" in response.answer


def test_empty_question_raises_error(relevant_chunks):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        build_evidence_answer("", relevant_chunks)


def test_invalid_min_score_raises_error(relevant_chunks):
    with pytest.raises(ValueError, match="min_score must be between 0 and 1"):
        build_evidence_answer(
            question="What is RAG?",
            chunks=relevant_chunks,
            min_score=1.5,
        )


def test_empty_chunks_returns_fallback():
    response = build_evidence_answer(
        question="What is RAG?",
        chunks=[],
    )

    assert response.citations == []
    assert response.confidence == 0.0
