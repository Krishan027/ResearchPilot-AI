
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


client = TestClient(app)


@patch("app.api.answer.answer_pdf_question")
def test_answer_endpoint_success(mock_answer):
    mock_answer.return_value = {
        "question": "What is RAG?",
        "answer": "RAG retrieves relevant evidence.",
        "citations": [
            {
                "source": "test_document.pdf",
                "page_number": 1,
                "chunk_id": "chunk-1",
            }
        ],
        "confidence": 0.85,
    }

    response = client.post(
        "/api/answer",
        json={
            "pdf_path": "test_document.pdf",
            "question": "What is RAG?",
            "top_k": 3,
            "min_score": 0.1,
        },
    )

    assert response.status_code == 200
    assert response.json()["question"] == "What is RAG?"
    assert response.json()["citations"][0]["page_number"] == 1


def test_answer_endpoint_rejects_invalid_top_k():
    response = client.post(
        "/api/answer",
        json={
            "pdf_path": "test_document.pdf",
            "question": "What is RAG?",
            "top_k": 0,
            "min_score": 0.1,
        },
    )

    assert response.status_code == 422
