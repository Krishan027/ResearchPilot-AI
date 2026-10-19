
from unittest.mock import Mock

import pytest

from app.llm.answer_generator import AnswerGenerator
from app.models.chunk import DocumentChunk


@pytest.fixture
def generator():
    instance = AnswerGenerator()
    instance.ollama = Mock()
    return instance


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


def test_empty_question_raises_error(generator, relevant_chunks):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        generator.generate("   ", relevant_chunks)


def test_empty_chunks_return_fallback(generator):
    response = generator.generate("What is RAG?", [])

    assert response.citations == []
    assert response.confidence == 0.0
    assert "could not find relevant evidence" in response.answer
    generator.ollama.generate_answer.assert_not_called()


def test_generator_includes_evidence_in_prompt(
    generator, relevant_chunks
):
    generator.ollama.generate_answer.return_value = (
        "RAG retrieves relevant documents before generating an answer [1]."
    )

    response = generator.generate("What is RAG?", relevant_chunks)

    prompt = generator.ollama.generate_answer.call_args.args[0]

    assert "What is RAG?" in prompt
    assert relevant_chunks[0].text in prompt
    assert relevant_chunks[1].text in prompt
    assert "PDF EXCERPTS:" in prompt
    assert len(response.citations) == 2
    assert response.citations[0].chunk_id == "chunk-1"


def test_invalid_citation_marker_is_flagged(
    generator, relevant_chunks
):
    generator.ollama.generate_answer.return_value = (
        "RAG retrieves relevant documents [9]."
    )

    response = generator.generate("What is RAG?", relevant_chunks)

    assert "invalid citation markers" in response.answer
    assert "[9]" in response.answer


def test_confidence_uses_average_retrieval_score(
    generator, relevant_chunks
):
    generator.ollama.generate_answer.return_value = (
        "RAG uses retrieved evidence [1]."
    )

    response = generator.generate("What is RAG?", relevant_chunks)

    assert response.confidence == pytest.approx(0.775)


def test_ollama_error_is_propagated(generator, relevant_chunks):
    generator.ollama.generate_answer.side_effect = RuntimeError(
        "Ollama unavailable"
    )

    with pytest.raises(RuntimeError, match="Ollama unavailable"):
        generator.generate("What is RAG?", relevant_chunks)
