
import pytest
from pydantic import ValidationError

from app.schemas.answer import AnswerResponse, Citation


def test_valid_answer_response():
    response = AnswerResponse(
        question="What is RAG?",
        answer="RAG retrieves relevant evidence before generating an answer.",
        citations=[
            Citation(
                source="test_document.pdf",
                page_number=1,
                chunk_id="chunk-1",
            )
        ],
        confidence=0.9,
    )

    assert response.citations[0].page_number == 1
    assert response.confidence == 0.9


def test_invalid_page_number():
    with pytest.raises(ValidationError):
        Citation(
            source="test_document.pdf",
            page_number=0,
            chunk_id="chunk-1",
        )


def test_invalid_confidence():
    with pytest.raises(ValidationError):
        AnswerResponse(
            question="What is RAG?",
            answer="A test answer.",
            confidence=1.5,
        )


def test_citations_default_to_empty():
    response = AnswerResponse(
        question="What is RAG?",
        answer="A test answer.",
        confidence=0.5,
    )

    assert response.citations == []
