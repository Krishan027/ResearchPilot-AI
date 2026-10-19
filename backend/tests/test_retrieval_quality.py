
from pathlib import Path

from app.retrieval.pipeline import search_pdf


def test_rag_question_retrieves_page_one():
    pdf_path = Path(__file__).parents[1] / "test_document.pdf"

    results = search_pdf(
        pdf_path=str(pdf_path),
        query="What is Retrieval Augmented Generation?",
        top_k=3,
    )

    assert results, "Expected at least one search result"
    assert results[0]["page_number"] == 1
