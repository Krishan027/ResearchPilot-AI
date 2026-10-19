
from unittest.mock import patch

from app.models.chunk import DocumentChunk
from app.schemas.answer import AnswerResponse, Citation
from app.retrieval.answer_pipeline import answer_pdf_question


@patch("app.retrieval.answer_pipeline.answer_generator.generate")
@patch("app.retrieval.answer_pipeline.search_pdf")
def test_answer_pdf_question_returns_citations(mock_search_pdf, mock_generate):
    mock_search_pdf.return_value = [
        {
            "chunk_id": "chunk-1",
            "source": "test_document.pdf",
            "page_number": 1,
            "text": (
                "RAG retrieves relevant evidence before "
                "generating an answer."
            ),
            "score": 0.85,
        }
    ]
    mock_generate.return_value = AnswerResponse(
        question="What is RAG?",
        answer="RAG retrieves relevant evidence [1].",
        citations=[
            Citation(
                source="test_document.pdf",
                page_number=1,
                chunk_id="chunk-1",
                text="RAG retrieves relevant evidence before generating an answer.",
            )
        ],
        confidence=0.85,
    )

    response = answer_pdf_question(
        pdf_path="test_document.pdf",
        question="What is RAG?",
        min_score=0.25,
    )

    assert response.question == "What is RAG?"
    assert len(response.citations) == 1
    assert response.citations[0].source == "test_document.pdf"
    assert response.citations[0].page_number == 1
    mock_generate.assert_called_once()

    mock_search_pdf.assert_called_once()


@patch("app.retrieval.answer_pipeline.search_pdf")
def test_answer_pipeline_handles_no_results(mock_search_pdf):
    mock_search_pdf.return_value = []

    response = answer_pdf_question(
        pdf_path="test_document.pdf",
        question="What is RAG?",
    )

    assert response.citations == []
    assert response.confidence == 0.0
    mock_search_pdf.assert_called_once()
