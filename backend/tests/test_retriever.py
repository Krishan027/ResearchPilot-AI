
import pytest

from app.models.chunk import DocumentChunk
from app.retrieval.retriever import SemanticRetriever


class FakeEmbedder:
    """A small predictable embedder for testing."""

    def embed_text(self, text: str) -> list[float]:
        vectors = {
            "Python programming": [1.0, 0.0],
            "Learn Python coding": [0.9, 0.1],
            "Sunny weather today": [0.0, 1.0],
        }
        return vectors[text]


@pytest.fixture
def retriever():
    instance = SemanticRetriever.__new__(SemanticRetriever)
    instance.embedder = FakeEmbedder()
    return instance


@pytest.fixture
def chunks():
    return [
        DocumentChunk(
            chunk_id="chunk-1",
            source="python.pdf",
            page_number=1,
            chunk_index=0,
            text="Learn Python coding",
        ),
        DocumentChunk(
            chunk_id="chunk-2",
            source="weather.pdf",
            page_number=2,
            chunk_index=1,
            text="Sunny weather today",
        ),
    ]


def test_retrieve_ranks_relevant_chunks_first(retriever, chunks):
    results = retriever.retrieve(
        "Python programming",
        chunks,
        top_k=2,
    )

    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["score"] > results[1]["score"]


def test_retrieve_respects_top_k(retriever, chunks):
    results = retriever.retrieve(
        "Python programming",
        chunks,
        top_k=1,
    )

    assert len(results) == 1


def test_retrieve_preserves_source_and_page(retriever, chunks):
    results = retriever.retrieve(
        "Python programming",
        chunks,
        top_k=1,
    )

    assert results[0]["source"] == "python.pdf"
    assert results[0]["page_number"] == 1


def test_empty_query_raises_error(retriever, chunks):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("   ", chunks)


def test_invalid_top_k_raises_error(retriever, chunks):
    with pytest.raises(ValueError, match="top_k must be positive"):
        retriever.retrieve("Python programming", chunks, top_k=0)


def test_empty_chunks_returns_empty_list(retriever):
    results = retriever.retrieve("Python programming", [])

    assert results == []
