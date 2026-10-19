
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_uploaded_document_not_found():
    response = client.post(
        "/api/documents/missing-document.pdf/answer",
        json={
            "question": "What is RAG?",
            "top_k": 3,
            "min_score": 0.1,
        },
    )

    # Print details if the request fails unexpectedly.
    if response.status_code != 404:
        print("Status:", response.status_code)
        print("Response:", response.json())

    assert response.status_code == 404


def test_invalid_document_id():
    response = client.post(
        "/api/documents/invalid.txt/answer",
        json={
            "question": "What is RAG?",
            "top_k": 3,
            "min_score": 0.1,
        },
    )

    # Print details if the request fails unexpectedly.
    if response.status_code != 400:
        print("Status:", response.status_code)
        print("Response:", response.json())

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid document ID."
